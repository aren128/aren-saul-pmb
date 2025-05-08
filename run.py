from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
from werkzeug.utils import secure_filename
import os
from models import db, Registration, init_db
from datetime import datetime
from auth import auth

# Add these configurations
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pmb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register the auth blueprint
app.register_blueprint(auth, url_prefix='/auth')

@app.route('/')
@app.route('/home')
def home():
    # Get latest registrations for display
    registrations = Registration.query.order_by(Registration.created_at.desc()).limit(5).all()
    return render_template('index.html', registrations=registrations)

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('auth.login'))  # Added missing parenthesis
        
    # Get all registrations
    registrations = Registration.query.order_by(Registration.created_at.desc()).all()
    return render_template('admin_dashboard.html', registrations=registrations)

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    # Get registration data for current user
    registration = Registration.query.filter_by(user_id=session['user_id']).first()
    return render_template('dashboard.html', registration=registration)

@app.route('/registration_form')
def registration_form():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('registration_form.html')

@app.route('/register_student', methods=['POST'])
def register_student():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        try:
            # Handle file uploads
            ijazah = request.files['ijazah']
            foto = request.files['foto']
            
            # Save files with secure filenames
            ijazah_filename = secure_filename(ijazah.filename)
            foto_filename = secure_filename(foto.filename)
            
            ijazah.save(os.path.join(app.config['UPLOAD_FOLDER'], ijazah_filename))
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
            
            # Create new registration
            new_registration = Registration(
                user_id=session['user_id'],
                full_name=request.form['full_name'],
                birth_date=datetime.strptime(request.form['birth_date'], '%Y-%m-%d'),
                gender=request.form['gender'],
                phone=request.form['phone'],
                address=request.form['address'],
                previous_school=request.form['previous_school'],
                ijazah_file=ijazah_filename,
                foto_file=foto_filename,
                parent_name=request.form['parent_name'],
                parent_phone=request.form['parent_phone'],
                parent_occupation=request.form['parent_occupation'],
                status='pending'
            )
            
            db.session.add(new_registration)
            db.session.commit()
            
            flash('Pendaftaran berhasil dikirim!', 'success')
            return redirect(url_for('user_dashboard'))  # This will show the info in dashboard
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('registration_form'))

# Add routes for approve/reject functionality
@app.route('/update_status/<int:reg_id>', methods=['POST'])
def update_status(reg_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    registration = Registration.query.get_or_404(reg_id)
    status = request.form.get('status')
    
    if status in ['approved', 'rejected', 'pending']:
        registration.status = status
        db.session.commit()
        flash(f'Status updated to {status}', 'success')
        return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid status'}), 400

if __name__ == '__main__':
    app.run(debug=True)