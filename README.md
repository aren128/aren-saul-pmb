# PMB (Penerimaan Mahasiswa Baru) System

## Overview
A web-based Student Admission System built with Flask that manages the entire admission process from registration to payment verification.

## Features
- User Authentication (Student & Admin)
- Online Registration Form
- Document Upload (Photo & Certificate)
- Payment Processing & Verification
- Admin Dashboard
- Real-time Status Updates
- Automatic Notifications

## Technology Stack
- **Backend:** Python Flask
- **Database:** SQLAlchemy
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Icons:** Font Awesome 5

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/pmb-system.git
cd pmb-system
```

2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize database
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application
```bash
python run.py
```

## Usage
- Access the application at `http://localhost:5000`
- Register as a new student
- Complete the registration form
- Upload required documents
- Make payment and upload proof
- Track application status

## Project Structure
```
pmb/
├── auth/
│   ├── __init__.py
│   └── routes.py
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── templates/
│   ├── auth/
│   └── *.html
├── models.py
├── run.py
└── requirements.txt
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.



## Contact
Aren Saul - [za086268@gmail.com]
