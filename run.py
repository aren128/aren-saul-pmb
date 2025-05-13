from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import os
from models import db, Registration, User, Notification, init_db
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
    
    registrations = Registration.query.order_by(Registration.created_at.desc()).limit(5).all()
    return render_template('index.html', registrations=registrations)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.is_admin() and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
            
        flash('Invalid credentials or not authorized!', 'danger')
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get all registrations
    registrations = Registration.query.order_by(Registration.created_at.desc()).all()
    
    return render_template('admin_dashboard.html', registrations=registrations)

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    # Get registration data for current user
    registration = Registration.query.filter_by(user_id=session['user_id']).first()
    
    # Get unread notifications
    notifications = Notification.query.filter_by(
        user_id=session['user_id'],
        is_read=False
    ).order_by(Notification.created_at.desc()).all()
    
    # Mark notifications as read
    for notification in notifications:
        notification.is_read = True
    db.session.commit()
    
    return render_template('dashboard.html', 
                         registration=registration,
                         notifications=notifications)

@app.route('/registration_form')
def registration_form():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'warning')
        return redirect(url_for('auth.login'))
        
    user = User.query.get(session['user_id'])
    if user.has_registration():
        flash('Anda sudah melakukan pendaftaran!', 'warning')
        return redirect(url_for('user_dashboard'))
        
    return render_template('registration_form.html', user=user)

@app.route('/register_student', methods=['POST'])
def register_student():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'warning')
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
                school_time=request.form['school_time'],  # Add this line
                ijazah_file=ijazah_filename,
                foto_file=foto_filename,
                parent_name=request.form['parent_name'],
                parent_phone=request.form['parent_phone'],
                parent_occupation=request.form['parent_occupation'],
                status='pending'
            )
            
            db.session.add(new_registration)
            db.session.commit()
            
            flash('Pendaftaran berhasil dikirim! Silakan pantau status pendaftaran Anda.', 'success')
            return redirect(url_for('user_dashboard'))
            
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            return redirect(url_for('registration_form'))

# Add this route before the existing routes
@app.route('/registration/<int:id>')
def view_registration(id):
    if session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('auth.login'))
        
    registration = Registration.query.get_or_404(id)
    return render_template('view_registration.html', registration=registration)

# Add routes for approve/reject functionality
@app.route('/update_status/<int:reg_id>', methods=['POST'])
def update_status(reg_id):
    if session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('auth.login'))
        
    registration = Registration.query.get_or_404(reg_id)
    status = request.form.get('status')
    
    if status in ['approved', 'rejected']:
        registration.status = status
        registration.updated_at = datetime.utcnow()
        
        # Create notification message
        if status == 'approved':
            message = "Selamat! Pendaftaran Anda telah diterima."
            category = "success"
        else:
            reason = request.form.get('reason')
            custom_reason = request.form.get('customReason')
            
            # Get the final reason text
            if reason == 'custom':
                final_reason = custom_reason
            else:
                final_reason = reason
                
            message = f"Maaf, pendaftaran Anda ditolak. Alasan: {final_reason}"
            category = "danger"
            
        # Save notification
        notification = Notification(
            user_id=registration.user_id,
            message=message,
            category=category
        )
        
        db.session.add(notification)
        db.session.commit()
        
        status_text = 'diterima' if status == 'approved' else 'ditolak'
        flash(f'Status pendaftaran telah diubah menjadi {status_text}', 'success')
        return redirect(url_for('view_registration', id=reg_id))
    
    flash('Status tidak valid!', 'danger')
    return redirect(url_for('view_registration', id=reg_id))

if __name__ == '__main__':
    app.run(debug=True)