from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    registrations = db.relationship('Registration', backref='user', lazy=True)

    def __init__(self, username, email, password, role='user'):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def is_admin(self):
        return self.role == 'admin'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class UserRegistration(db.Model):
    __tablename__ = 'user_registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True)
    is_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token

    def confirm(self):
        self.is_confirmed = True
        self.confirmed_at = datetime.utcnow()

class Registration(db.Model):
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    previous_school = db.Column(db.String(100), nullable=False)
    ijazah_file = db.Column(db.String(255), nullable=False)
    foto_file = db.Column(db.String(255), nullable=False)
    parent_name = db.Column(db.String(100), nullable=False)
    parent_phone = db.Column(db.String(20), nullable=False)
    parent_occupation = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id, full_name, birth_date, gender, phone, address, 
                 previous_school, ijazah_file, foto_file, parent_name, 
                 parent_phone, parent_occupation, status='pending'):
        self.user_id = user_id
        self.full_name = full_name
        self.birth_date = birth_date
        self.gender = gender
        self.phone = phone
        self.address = address
        self.previous_school = previous_school
        self.ijazah_file = ijazah_file
        self.foto_file = foto_file
        self.parent_name = parent_name
        self.parent_phone = parent_phone
        self.parent_occupation = parent_occupation
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'birth_date': self.birth_date.strftime('%Y-%m-%d'),
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address,
            'previous_school': self.previous_school,
            'ijazah_file': self.ijazah_file,
            'foto_file': self.foto_file,
            'parent_name': self.parent_name,
            'parent_phone': self.parent_phone,
            'parent_occupation': self.parent_occupation,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        if not User.query.filter_by(role='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

# Helper function to create a new user
def create_user(username, email, password, role='user'):
    user = User(
        username=username,
        email=email,
        password=password,
        role=role
    )
    db.session.add(user)
    db.session.commit()
    return user