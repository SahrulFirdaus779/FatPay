import streamlit as st
import pandas as pd
from datetime import datetime

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="FatPay - Sistem Pembayaran Sekolah Digital",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Kustom untuk Menyembunyikan Menu Otomatis Streamlit ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        div[data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Logo dan Judul Sidebar ---
# st.sidebar.image("fmlagi.png", use_container_width=True)
st.sidebar.title("Navigasi FatPay")

# --- Inisialisasi Session State untuk Halaman ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Beranda"

# --- Fungsi untuk Mengubah Halaman ---
def set_page(page_name):
    st.session_state.current_page = page_name

# --- Sidebar Navigasi ---
st.sidebar.button("Beranda", on_click=set_page, args=("Beranda",), use_container_width=True)
st.sidebar.button("Dashboard", on_click=set_page, args=("Dashboard",), use_container_width=True)
st.sidebar.markdown("---")
st.sidebar.button("Pembayaran Baru", on_click=set_page, args=("Pembayaran Baru",), type="primary", use_container_width=True)
# --- TAMBAH TOMBOL KWITANSI DI SINI (Opsional, jika ingin bisa diakses dari sidebar) ---
# st.sidebar.button("Lihat Kwitansi Terakhir", on_click=set_page, args=("Kwitansi",), use_container_width=True)
st.sidebar.markdown("---")
st.sidebar.subheader("Riwayat Pembayaran")
st.sidebar.button("Riwayat SPP", on_click=set_page, args=("Riwayat SPP",), use_container_width=True)
st.sidebar.button("Riwayat UTS", on_click=set_page, args=("Riwayat UTS",), use_container_width=True)
st.sidebar.button("Riwayat UAS", on_click=set_page, args=("Riwayat UAS",), use_container_width=True)


# --- Pemrosesan Halaman Berdasarkan Session State ---
if st.session_state.current_page == "Beranda":
    st.title("Selamat Datang di FatPay 💸")
    st.markdown("""
    FatPay adalah aplikasi berbasis Streamlit yang dirancang untuk memudahkan proses administrasi pembayaran sekolah (SPP, UTS, UAS) di Yayasan Fathan Mubina.
    Aplikasi ini membantu sekolah dalam mencatat pembayaran siswa, mengirim notifikasi otomatis, dan mengelola riwayat pembayaran secara efisien.

    ### ✨ Fitur Utama:
    - **Pencatatan Pembayaran Instan:** Catat pembayaran SPP, UTS, dan UAS siswa dengan cepat dan akurat melalui formulir yang intuitif, kini dengan fitur kode unik siswa dan input pembayaran dinamis.
    - **Riwayat Pembayaran Lengkap dan Terstruktur:** Akses, kelola, dan pantau seluruh histori pembayaran siswa dalam satu tempat, dengan data yang terpisah untuk setiap jenis pembayaran.
    - **Dashboard Analitik Sederhana:** Dapatkan gambaran umum dan ringkasan data pembayaran sekolah secara keseluruhan untuk pemantauan keuangan yang lebih baik.
    - **Fungsi Edit & Hapus Data:** Perbarui atau hapus data pembayaran yang sudah tercatat dengan mudah.
    """)
    # st.image("fmlagi.png", width=300)

elif st.session_state.current_page == "Dashboard":
    from pages import dashboard
    dashboard.show_dashboard()

elif st.session_state.current_page == "Pembayaran Baru":
    from pages import payment_form
    payment_form.show_payment_form()

# --- TAMBAH LOGIKA UNTUK HALAMAN KWITANSI BARU ---
elif st.session_state.current_page == "Kwitansi":
    from pages import receipt_display
    receipt_display.show_receipt_page()

elif st.session_state.current_page == "Riwayat SPP":
    from pages import spp_pay
    spp_pay.show_spp_history()
elif st.session_state.current_page == "Riwayat UTS":
    from pages import uts_pay
    uts_pay.show_uts_history()
elif st.session_state.current_page == "Riwayat UAS":
    from pages import uas_pay
    uas_pay.show_uas_history()