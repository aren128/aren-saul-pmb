# Sistem Penerimaan Mahasiswa Baru (PMB)

## 📋 Overview
Sistem informasi penerimaan mahasiswa baru berbasis web yang dibangun menggunakan Flask. Sistem ini mengelola seluruh proses penerimaan mahasiswa dari pendaftaran hingga verifikasi pembayaran.

## ✨ Fitur Utama
- 🔐 Autentikasi Multi-User (Mahasiswa & Admin)
- 📝 Formulir Pendaftaran Online
- 📎 Upload Dokumen (Foto & Ijazah)
- 💳 Proses & Verifikasi Pembayaran
- 📊 Dashboard Admin
- 🔄 Update Status Real-time
- 📱 Responsif Mobile-Friendly
- 📧 Notifikasi Otomatis

## 🛠 Tech Stack
- **Backend:** Python Flask
- **Database:** SQLAlchemy (MySQL)
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **UI Components:** Font Awesome 5
- **Security:** Flask-Login, Werkzeug Security

## 🚀 Instalasi

### Prasyarat
- Python 3.8+
- MySQL/MariaDB
- Git

### Langkah Instalasi

1. Clone repository
```bash
git clone https://github.com/yourusername/pmb-system.git
cd pmb-system
```

2. Buat virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Konfigurasi database
```bash
# Buat file .env dan isi dengan konfigurasi berikut
DATABASE_URL=mysql://username:password@localhost/pmb_db
SECRET_KEY=your-secret-key
```

5. Inisialisasi database
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Jalankan aplikasi
```bash
python run.py
```

## 📱 Cara Penggunaan

### Untuk Calon Mahasiswa
1. Akses aplikasi di `http://localhost:5000`
2. Registrasi akun baru
3. Login dan lengkapi formulir pendaftaran
4. Upload dokumen yang diperlukan:
   - Pas foto 4x6
   - Ijazah/SKL
   - Kartu identitas
5. Lakukan pembayaran dan upload bukti
6. Pantau status pendaftaran di dashboard

### Untuk Admin
1. Akses halaman admin di `http://localhost:5000/admin`
2. Login dengan kredensial admin
3. Kelola data pendaftar
4. Verifikasi dokumen dan pembayaran
5. Update status pendaftaran

## 📁 Struktur Proyek
```
pmb/
├── auth/                  # Autentikasi
│   ├── __init__.py
│   └── routes.py
├── static/               # Aset statis
│   ├── css/
│   ├── js/
│   └── uploads/         # File upload
├── templates/           # Template HTML
│   ├── auth/
│   └── *.html
├── models.py           # Model database
├── run.py             # Entry point
└── requirements.txt   # Dependencies
```

## 💡 Fitur Mendatang
- [ ] Integrasi pembayaran online
- [ ] Sistem ujian online
- [ ] Export data ke Excel/PDF
- [ ] API untuk integrasi sistem lain
- [ ] Dashboard analitik

## 🤝 Kontribusi
Kontribusi selalu diterima. Untuk perubahan besar, silakan buka issue terlebih dahulu untuk mendiskusikan perubahan yang diinginkan.

## 📝 Lisensi
[MIT](https://choosealicense.com/licenses/mit/)

## 📞 Kontak
Aren Saul - za086268@gmail.com

## 🙏 Acknowledgments
- Flask Team
- Bootstrap Team
- Font Awesome
- Seluruh kontributor
