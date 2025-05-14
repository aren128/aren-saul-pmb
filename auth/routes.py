from flask import render_template, redirect, url_for, request, flash, session
from werkzeug.security import check_password_hash
from . import auth
from models import User, db, create_user

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Password tidak cocok!', 'danger')
            return render_template('auth/register.html')

        if User.get_by_username(username):
            flash('Username sudah digunakan!', 'danger')
            return render_template('auth/register.html')

        if User.get_by_email(email):
            flash('Email sudah terdaftar!', 'danger')
            return render_template('auth/register.html')

        try:
            # Create new user
            user = create_user(username, email, password)
            
            # Automatically log in the user after registration
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            flash('Registrasi berhasil! Silakan lengkapi formulir pendaftaran.', 'success')
            # Redirect to registration form immediately
            return redirect(url_for('registration_form'))
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')

    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.authenticate(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login berhasil!', 'success-permanent')
            if user.is_admin():
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        flash('Username atau password salah!', 'danger-permanent')

    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('Berhasil logout!', 'success-permanent')
    return redirect(url_for('auth.login'))