💸 FatPay - Sistem Pembayaran Sekolah Digital
FatPay adalah aplikasi berbasis Streamlit yang dirancang untuk memudahkan proses administrasi pembayaran sekolah (SPP, UTS, UAS) di Yayasan Fathan Mubina. Aplikasi ini membantu sekolah dalam mencatat pembayaran siswa, mengirim notifikasi otomatis, dan mengelola riwayat pembayaran secara efisien.

✨ Fitur Utama
Pencatatan Pembayaran Instan: Catat pembayaran SPP, UTS, dan UAS siswa dengan cepat dan akurat melalui formulir yang intuitif.

Notifikasi Otomatis via WhatsApp: Kirim bukti pembayaran dan informasi penting langsung ke nomor WhatsApp orang tua secara instan, meningkatkan komunikasi dan transparansi.

Riwayat Pembayaran Lengkap dan Terstruktur: Akses, kelola, dan pantau seluruh histori pembayaran siswa dalam satu tempat, dengan data yang terpisah untuk setiap jenis pembayaran.

Dashboard Analitik Sederhana: Dapatkan gambaran umum dan ringkasan data pembayaran sekolah secara keseluruhan untuk pemantauan keuangan yang lebih baik.

Fungsi Edit & Hapus Data: Perbarui atau hapus data pembayaran yang sudah tercatat dengan mudah.

🚀 Instalasi dan Penggunaan
Ikuti langkah-langkah di bawah ini untuk mengatur dan menjalankan aplikasi FatPay di lingkungan lokal Anda.

📋 Prerequisites
Pastikan Anda telah menginstal Python (versi 3.7+) di sistem Anda.

📦 Instalasi
Buat Struktur Folder:
Buat folder utama untuk proyek Anda (misalnya, FatPay/). Di dalamnya, buat subfolder bernama pages/.

Struktur proyek akan terlihat seperti ini:

FatPay/
├── app.py
├── pages/
│   ├── dashboard.py
│   ├── spp_pay.py
│   ├── uts_pay.py
│   └── uas_pay.py
├── fmlagi.png             (file logo Anda)
├── spp_data.csv           (akan dibuat otomatis atau Anda bisa buat file kosong)
├── uts_data.csv           (akan dibuat otomatis atau Anda bisa buat file kosong)
├── uas_data.csv           (akan dibuat otomatis atau Anda bisa buat file kosong)
└── requirements.txt

Tempatkan File Aplikasi:

Salin kode untuk app.py ke dalam folder FatPay/.

Salin kode untuk dashboard.py, spp_pay.py, uts_pay.py, dan uas_pay.py ke dalam folder FatPay/pages/.

Tempatkan file fmlagi.png (logo Anda) di folder FatPay/.

Buat file kosong bernama spp_data.csv, uts_data.csv, dan uas_data.csv di folder FatPay/ jika belum ada (aplikasi akan membuatnya secara otomatis saat ada data pertama).

Instal Dependensi:
Buka terminal atau command prompt Anda, navigasikan ke direktori utama proyek FatPay/, lalu jalankan perintah berikut untuk menginstal semua pustaka yang diperlukan:

pip install -r requirements.txt

🏃 Menjalankan Aplikasi
Dari direktori utama proyek FatPay/ di terminal atau command prompt Anda, jalankan perintah berikut:

streamlit run app.py

Ini akan membuka aplikasi FatPay di browser web default Anda.

💡 Cara Menggunakan Aplikasi
Navigasi Sidebar: Gunakan menu di sidebar kiri untuk beralih antara halaman Beranda (Landing Page), Dashboard, SPP Pay, UTS Pay, dan UAS Pay.

Halaman Beranda: Menampilkan informasi umum dan fitur utama FatPay.

Halaman Pembayaran (SPP/UTS/UAS Pay):

Isi detail pembayaran (NIS, Nama Siswa, Bulan/Ujian, Jumlah Pembayaran, Nomor WhatsApp Orang Tua).

Klik tombol "Simpan & Kirim Notifikasi" untuk mencatat pembayaran dan mengirim pesan WhatsApp.

Riwayat pembayaran akan ditampilkan di bagian bawah halaman.

Edit & Hapus Data:

Pilih data yang ingin diedit atau dihapus dari st.selectbox di bawah riwayat pembayaran.

Klik tombol "📝 Edit Data [Jenis Pembayaran]" untuk menampilkan formulir edit. Ubah data yang diperlukan, lalu klik "💾 Simpan Perubahan".

Klik tombol "🗑️ Hapus Data [Jenis Pembayaran]" untuk menghapus data yang dipilih.

Dashboard: Menampilkan ringkasan agregat dari semua data pembayaran yang tercatat di setiap jenis pembayaran.

© 2025 FatPay | Dibuat dengan ❤️ oleh Tim IT Fathan Mubina