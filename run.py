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

# Add to existing configurations
AVATAR_FOLDER = os.path.join('static', 'images', 'avatars')
app.config['AVATAR_FOLDER'] = AVATAR_FOLDER

# Create avatar directory if it doesn't exist
os.makedirs(os.path.join(app.static_folder, 'images', 'avatars'), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_avatar_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

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
        
    # Get user data
    user = User.query.get(session['user_id'])
    
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
                         user=user,  # Pass the user object
                         registration=registration,
                         notifications=notifications)

@app.route('/registration_form')
def registration_form():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'warning')
        return redirect(url_for('auth.login'))
        
    user = User.query.get(session['user_id'])
    if user.has_registration():
        flash('Anda sudah melakukan pendaftaran!', 'warning-permanent')
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
                school_time=request.form['school_time'],
                ijazah_file=ijazah_filename,
                foto_file=foto_filename,
                parent_name=request.form['parent_name'],
                parent_phone=request.form['parent_phone'],
                parent_occupation=request.form['parent_occupation'],
                faculty=request.form['faculty'],
                major=request.form['major'],
                religion=request.form['religion'],
                status='pending'
            )
            
            db.session.add(new_registration)
            db.session.commit()
            
            flash('Pendaftaran berhasil dikirim! Silakan pantau status pendaftaran Anda.', 'success permanent')
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
        # Update registration status
        registration.status = status
        registration.updated_at = datetime.utcnow()
        
        # Create notification message
        if status == 'approved':
            message = ("Selamat! Pendaftaran Anda telah diterima.\n"
                      "Silakan melakukan pembayaran untuk menyelesaikan proses pendaftaran.\n"
                      "Anda dapat melakukan pembayaran melalui menu Pembayaran.")
            category = "success"
        else:
            reason = request.form.get('reason')
            custom_reason = request.form.get('customReason')
            final_reason = custom_reason if reason == 'custom' else reason
            message = f"Maaf, pendaftaran Anda ditolak. Alasan: {final_reason}"
            category = "danger"
            
        # Create and save notification
        notification = Notification(
            user_id=registration.user_id,
            message=message,
            category=category
        )
        db.session.add(notification)
        
        # Commit all changes
        try:
            db.session.commit()
            status_text = 'diterima' if status == 'approved' else 'ditolak'
            flash(f'Status pendaftaran berhasil diubah menjadi {status_text}!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            
        return redirect(url_for('view_registration', id=reg_id))
    
    flash('Status tidak valid!', 'danger')
    return redirect(url_for('view_registration', id=reg_id))

@app.route('/upload_payment/<int:reg_id>', methods=['POST'])
def upload_payment(reg_id):
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'warning')
        return redirect(url_for('auth.login'))
        
    registration = Registration.query.get_or_404(reg_id)
    
    if registration.user_id != session['user_id']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('user_dashboard'))
        
    if 'payment_proof' not in request.files:
        flash('Tidak ada file yang diupload!', 'danger')
        return redirect(url_for('user_dashboard'))
        
    file = request.files['payment_proof']
    if file.filename == '':
        flash('Tidak ada file yang dipilih!', 'danger')
        return redirect(url_for('user_dashboard'))
        
    if file and allowed_file(file.filename):
        # Create payment_proofs directory if it doesn't exist
        upload_dir = os.path.join(app.static_folder, 'uploads', 'payment_proofs')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file
        filename = secure_filename(f"payment_{reg_id}_{int(datetime.utcnow().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}")
        file.save(os.path.join(upload_dir, filename))
        
        # Update registration payment status
        registration.payment_status = 'pending'
        registration.payment_proof = filename
        registration.payment_date = datetime.strptime(request.form['payment_date'], '%Y-%m-%dT%H:%M')
        db.session.commit()
        
        # Create notification for admin
        notification = Notification(
            user_id=User.query.filter_by(role='admin').first().id,
            message=f"Ada pembayaran baru dari {registration.full_name} yang perlu diverifikasi.",
            category="info"
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Bukti pembayaran berhasil diupload!', 'success permanent')
        return redirect(url_for('user_dashboard'))
        
    flash('Format file tidak diizinkan!', 'danger')
    return redirect(url_for('user_dashboard'))

@app.route('/update_payment/<int:reg_id>', methods=['POST'])
def update_payment(reg_id):
    if session.get('role') != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('auth.login'))
        
    registration = Registration.query.get_or_404(reg_id)
    payment_status = request.form.get('payment_status')
    payment_amount = float(request.form.get('payment_amount', 0))
    
    if payment_status in ['paid', 'unpaid']:
        registration.payment_status = payment_status
        registration.payment_amount = payment_amount if payment_status == 'paid' else 0
        
        # Create notification for user
        message = ""
        if payment_status == 'paid':
            registration.payment_date = datetime.utcnow()
            message = f"Pembayaran Anda sebesar Rp {payment_amount:,.2f} telah dikonfirmasi."
            category = "success"
        else:
            message = "Pembayaran Anda ditolak. Silakan upload ulang bukti pembayaran."
            category = "danger"
            
        notification = Notification(
            user_id=registration.user_id,
            message=message,
            category=category
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Status pembayaran berhasil diperbarui!', 'success permanent')
        return redirect(url_for('view_registration', id=reg_id))
    
    flash('Status pembayaran tidak valid!', 'danger')
    return redirect(url_for('view_registration', id=reg_id))

@app.route('/pembayaran')
def pembayaran():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'warning')
        return redirect(url_for('auth.login'))
        
    registration = Registration.query.filter_by(user_id=session['user_id']).first()
    if not registration:
        flash('Anda belum melakukan pendaftaran!', 'warning')
        return redirect(url_for('registration_form'))
        
    return render_template('pembayaran.html', registration=registration)

@app.route('/update_avatar', methods=['POST'])
def update_avatar():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'warning')
        return redirect(url_for('auth.login'))
        
    if 'avatar' not in request.files:
        flash('Tidak ada file yang dipilih!', 'danger')
        return redirect(url_for('user_dashboard'))
        
    file = request.files['avatar']
    if file.filename == '':
        flash('Tidak ada file yang dipilih!', 'danger')
        return redirect(url_for('user_dashboard'))
        
    if file and allowed_avatar_file(file.filename):
        # Delete old avatar if it's not the default
        user = User.query.get(session['user_id'])
        if user.avatar != 'default-avatar.png':
            old_avatar = os.path.join(app.config['AVATAR_FOLDER'], user.avatar)
            if os.path.exists(old_avatar):
                os.remove(old_avatar)
        
        # Save new avatar
        filename = secure_filename(f"avatar_{session['user_id']}_{int(datetime.utcnow().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}")
        file.save(os.path.join(app.config['AVATAR_FOLDER'], filename))
        
        # Update user avatar in database
        user.avatar = filename
        db.session.commit()
        
        flash('Avatar berhasil diperbarui!', 'success')
        return redirect(url_for('user_dashboard'))
        
    flash('Format file tidak diizinkan! Gunakan PNG, JPG, atau JPEG.', 'danger')
    return redirect(url_for('user_dashboard'))

@app.route('/progress_tracking')
def progress_tracking():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'warning')
        return redirect(url_for('auth.login'))
        
    registration = Registration.query.filter_by(user_id=session['user_id']).first()
    user = User.query.get(session['user_id'])
    
    return render_template('progress_tracking.html', 
                         registration=registration,
                         user=user)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')