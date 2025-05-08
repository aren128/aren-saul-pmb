from flask import Flask, render_template, session, redirect, url_for, request, flash
from auth import auth

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Register the auth blueprint
app.register_blueprint(auth, url_prefix='/auth')

@app.route('/')
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.register'))
    return render_template('layout.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('layout.html')

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')

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
        # Here you would typically save the form data to a database
        flash('Pendaftaran berhasil dikirim!', 'success')
        return redirect(url_for('user_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)