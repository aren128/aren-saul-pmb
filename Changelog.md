# 📝 Catatan Perubahan

## [v1.0.0] - 22 Mei 2024

### ✨ Fitur Baru

#### 🔒 Sistem Autentikasi
- Implementasi login multi-user
  ```python
  @auth.route('/login', methods=['GET', 'POST'])
  @auth.route('/admin/login', methods=['GET', 'POST'])
  ```
- Manajemen sesi dengan Flask-Login
- Proteksi route berdasarkan peran

#### 📋 Formulir Pendaftaran
- Wizard form dengan validasi
- Upload dokumen persyaratan
- Pilihan fakultas & program studi:
  - Fakultas Teknik
  - Fakultas Ekonomi
  - Fakultas Hukum
  - Fakultas Kedokteran
  - FISIP

#### 💰 Sistem Pembayaran
- Upload bukti pembayaran
- Panel verifikasi admin
- Status tracking realtime
- Notifikasi status pembayaran

#### 👤 Profil Pengguna
- Upload & crop avatar
- Update informasi pribadi
- Riwayat pendaftaran
- Status dokumen

### 🔧 Perbaikan Teknis

#### Backend (run.py)
- Implementasi blueprint auth
- Integrasi SQLAlchemy ORM
- File upload handling
- Session management

#### Database (models.py)
- Model User
- Model Registration
- Model Payment
- Relasi antar tabel

#### Frontend (templates/)
- Layout responsif (Bootstrap 5)
- Form validation (JavaScript)
- File preview
- Progress tracking

### 🐛 Bug Fixes
- Path upload file Windows
- Validasi ekstensi file
- Reset form setelah submit
- Refresh token keamanan

## [v0.1.0] - 21 Mei 2024

### 🏗 Initial Setup
- Struktur folder dasar:
  ```
  pmb/
  ├── auth/
  ├── static/
  │   ├── css/
  │   ├── js/
  │   └── uploads/
  ├── templates/
  ├── models.py
  └── run.py
  ```
- Konfigurasi Flask dasar
- Setup database SQLite
- Template auth dasar

### 📋 Todo
- [ ] Integrasi Midtrans
- [ ] Generate PDF dokumen
- [ ] Export data pendaftar
- [ ] API dokumentasi
- [ ] Dashboard statistik

### 🔨 Tech Stack
- Python 3.8+
- Flask 2.0+
- SQLAlchemy
- Bootstrap 5
- jQuery 3.6