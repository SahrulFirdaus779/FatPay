import streamlit as st
import os
# from PIL import Image # Opsional: jika Anda ingin mengimpor logo dari file lokal

# Konfigurasi halaman
# Meskipun ini adalah landing page, kita tetap mendefinisikan halaman lain
# agar sidebar navigasi Streamlit berfungsi dengan benar untuk multi-halaman.
PAGES = {
    "Beranda": "app.py", # Beranda (landing page ini)
    "Dashboard": "pages/dashboard.py",
    "SPP Pay": "pages/spp_pay.py",
    "UTS Pay": "pages/uts_pay.py",
    "UAS Pay": "pages/uas_pay.py"
}

st.set_page_config(
    page_title="FatPay - Landing Page", # Diubah judul halaman
    page_icon="fmlagi.png", # Diubah icon halaman
    layout="centered"
)


# Mengatur state halaman saat ini untuk navigasi Streamlit
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Beranda" # Set default page to Beranda


# Konten Halaman yang Dipilih
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    
if st.session_state.current_page == "Beranda":
    encoded_image = get_base64_image("fmlagi.png")
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{encoded_image}" alt="FatPay Logo" style="width: 150px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    # Konten tambahan di bawah menu navigasi sidebar
    st.sidebar.info(
        "Aplikasi ini dikembangkan untuk Yayasan Fathan Mubina. "
        "Terima kasih atas kepercayaan Anda! ✨"
    )

    st.title("👋 Selamat Datang di FatPay") # Judul utama

    # Divider
    st.markdown("---")

    # Konten sambutan
    st.markdown(
        """
        Assalamu'alaikum Warahmatullahi Wabarakatuh 🙏
        Selamat datang di **FatPay**, sistem pembayaran SPP digital untuk memudahkan proses pembayaran di Yayasan Fathan Mubina.

        Di aplikasi ini, Anda dapat:
        - Mencatat pembayaran SPP, UTS, dan UAS siswa secara efisien
        - Mengirim notifikasi otomatis ke WhatsApp orang tua
        - Melihat dan mengelola riwayat pembayaran

        Silakan navigasi ke menu di sebelah kiri untuk mulai menggunakan fitur aplikasi.
        """
    )
    # [Image of FatPay Illustration]
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    
if st.session_state.current_page == "Beranda":
    encoded_image = get_base64_image("workflow.png")
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{encoded_image}" alt="FatPay Logo" style="width: 300px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    # Footer
    st.markdown("---")
    st.caption("© 2025 FatPay | Dibuat dengan ❤️ oleh Tim IT Fathan Mubina")

elif st.session_state.current_page == "Dashboard":
    # Streamlit akan secara otomatis menemukan dan menjalankan pages/dashboard.py
    # jika session_state.current_page adalah "Dashboard"
    pass 
else:
    # Untuk halaman pembayaran lainnya (SPP Pay, UTS Pay, UAS Pay)
    # Streamlit akan secara otomatis menemukan dan menjalankan file di folder `pages`
    pass
