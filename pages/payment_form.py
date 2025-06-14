import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os # Untuk manipulasi path file
from fpdf import FPDF # Untuk membuat PDF

# --- Path File Data ---
STUDENT_DATA_PATH = 'student_data.csv'
SPP_DATA_PATH = 'spp_data.csv'
UTS_DATA_PATH = 'uts_data.csv'
UAS_DATA_PATH = 'uas_data.csv'

# Path untuk folder kwitansi
RECEIPT_FOLDER = os.path.join(os.path.dirname(__file__), 'kwitansi_pembayaran')

# Pastikan folder kwitansi ada
os.makedirs(RECEIPT_FOLDER, exist_ok=True)

# --- Fungsi Utility ---
@st.cache_data
def load_student_data():
    """Memuat data siswa dari CSV, hanya mengambil kode_unik dan nama_anak."""
    try:
        df = pd.read_csv(STUDENT_DATA_PATH)
        return df[['kode_unik', 'nama_anak']]
    except FileNotFoundError:
        st.error(f"File '{STUDENT_DATA_PATH}' tidak ditemukan. Pastikan sudah dibuat di folder utama FatPay.")
        return pd.DataFrame(columns=['kode_unik', 'nama_anak'])
    except Exception as e:
        st.error(f"Error saat memuat data siswa: {e}")
        return pd.DataFrame(columns=['kode_unik', 'nama_anak'])

@st.cache_data
def load_payment_data(file_path):
    """Memuat data pembayaran dari CSV, mengembalikan DataFrame kosong jika file tidak ditemukan."""
    try:
        df = pd.read_csv(file_path)
        if 'Tanggal' in df.columns:
            df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
        return df
    except FileNotFoundError:
        default_columns = ['Nomor Pembayaran', 'Tanggal', 'Kode Unik Siswa', 'Nama Siswa',
                           'Jenis Pembayaran', 'Bulan/Ujian', 'Jumlah', 'Diskon', 'Grandtotal']
        return pd.DataFrame(columns=default_columns)
    except Exception as e:
        st.error(f"Error saat memuat data dari '{file_path}': {e}")
        default_columns = ['Nomor Pembayaran', 'Tanggal', 'Kode Unik Siswa', 'Nama Siswa',
                           'Jenis Pembayaran', 'Bulan/Ujian', 'Jumlah', 'Diskon', 'Grandtotal']
        return pd.DataFrame(columns=default_columns)

def save_payment_data(df, file_path):
    """Menyimpan data pembayaran ke CSV."""
    try:
        df.to_csv(file_path, index=False)
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Error saat menyimpan data ke '{file_path}': {e}")

# Fungsi untuk membuat dan menyimpan kwitansi PDF
def generate_receipt_pdf(receipt_data):
    pdf = FPDF(format='A5')
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Header
    pdf.cell(0, 10, "YAYASAN FATHAN MUBINA", align='C', ln=True)
    pdf.ln(5) # Spasi

    pdf.set_font("Arial", size=10)
    pdf.cell(0, 7, f"Nomor Pembayaran: {receipt_data['payment_id']}", ln=True)
    pdf.cell(0, 7, f"Tanggal: {receipt_data['payment_date'].strftime('%d %B %Y')}", ln=True)
    pdf.cell(0, 7, f"Siswa: {receipt_data['current_nama_siswa']} (Kode Unik: {receipt_data['current_kode_unik']})", ln=True)
    if receipt_data['optional_notes']:
        pdf.cell(0, 7, f"Keterangan: {receipt_data['optional_notes']}", ln=True)
    pdf.ln(5)

    # Detail Pembayaran
    pdf.set_font("Arial", 'B', size=10)
    pdf.cell(0, 7, "DETAIL PEMBAYARAN:", ln=True)
    pdf.set_font("Arial", size=10)
    for item in receipt_data['receipt_items']:
        pdf.cell(0, 7, f"- {item['jenis']} ({item['bulan_ujian']}): Rp {item['jumlah']:,.0f} (Diskon: Rp {item['diskon']:,.0f}) -> Rp {item['subtotal_item']:,.0f}", ln=True)
    pdf.ln(5)

    # Ringkasan Total
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 7, f"Subtotal: Rp {receipt_data['total_jumlah_item']:,.0f}", ln=True)
    pdf.cell(0, 7, f"Diskon Total: Rp {receipt_data['total_diskon_item']:,.0f}", ln=True)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, f"GRANDTOTAL: Rp {receipt_data['grandtotal']:,.0f}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 7, f"Metode Pembayaran: {receipt_data['jenis_pembayaran_final']}", ln=True)
    pdf.ln(10)

    pdf.cell(0, 7, "Terima kasih atas kepercayaan Anda!", align='C', ln=True)

    # Nama file
    filename = f"Kwitansi_Pembayaran_{receipt_data['payment_id']}.pdf"
    file_path = os.path.join(RECEIPT_FOLDER, filename)

    try:
        pdf.output(file_path)
        return file_path
    except Exception as e:
        st.error(f"Gagal membuat atau menyimpan PDF: {e}")
        return None

# --- Tampilan Formulir Pembayaran ---

def show_payment_form():
    st.title("Formulir Pembayaran Baru")

    # Inisialisasi session state baru untuk mengontrol tampilan kwitansi
    if 'show_receipt' not in st.session_state:
        st.session_state.show_receipt = False
    if 'receipt_data' not in st.session_state:
        st.session_state.receipt_data = {}

    # Inisialisasi session state lainnya jika belum ada
    if 'payment_id' not in st.session_state:
        st.session_state.payment_id = f"TRX-{uuid.uuid4().hex[:8].upper()}"
    if 'payment_date' not in st.session_state:
        st.session_state.payment_date = datetime.now().date()
    if 'optional_notes' not in st.session_state:
        st.session_state.optional_notes = ""
    if 'kode_unik_input' not in st.session_state:
        st.session_state.kode_unik_input = ""
    if 'found_nama_siswa' not in st.session_state:
        st.session_state.found_nama_siswa = ""
    if 'current_kode_unik' not in st.session_state:
        st.session_state.current_kode_unik = ""
    if 'payment_items' not in st.session_state:
        st.session_state.payment_items = []
    if 'item_keys_counter' not in st.session_state:
        st.session_state.item_keys_counter = 0

    student_df = load_student_data()

    # --- Bagian Identifikasi Siswa ---
    # Tampilkan form hanya jika kwitansi tidak sedang ditampilkan
    if not st.session_state.show_receipt:
        st.header("1. Identifikasi Siswa")
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Nomor Pembayaran", value=st.session_state.payment_id, disabled=True, key="payment_id_display")
            st.text_input("Keterangan (Optional)", value=st.session_state.optional_notes, key="optional_notes_input")
            st.session_state.optional_notes = st.session_state.optional_notes_input

        with col2:
            st.session_state.payment_date = st.date_input("Tanggal Transaksi", value=st.session_state.payment_date, key="payment_date_input")

        st.subheader("Pencarian Siswa")
        col_siswa_1, col_siswa_2 = st.columns([1, 2])

        def _update_student_info_callback(df_students):
            kode_unik = st.session_state.kode_unik_entry.strip()
            if kode_unik:
                found_student = df_students[df_students['kode_unik'] == kode_unik]
                if not found_student.empty:
                    st.session_state.found_nama_siswa = found_student['nama_anak'].iloc[0]
                    st.session_state.current_kode_unik = kode_unik
                    st.success(f"Siswa ditemukan: {st.session_state.found_nama_siswa}")
                else:
                    st.warning("Kode Unik Siswa tidak ditemukan.")
                    st.session_state.found_nama_siswa = ""
                    st.session_state.current_kode_unik = ""
            else:
                st.session_state.found_nama_siswa = ""
                st.session_state.current_kode_unik = ""

        with col_siswa_1:
            st.text_input(
                "Masukkan Kode Unik Siswa",
                value=st.session_state.kode_unik_input,
                key="kode_unik_entry",
                on_change=_update_student_info_callback,
                args=(student_df,)
            ).strip()
            st.session_state.kode_unik_input = st.session_state.kode_unik_entry

        if st.session_state.kode_unik_input and (not st.session_state.found_nama_siswa or st.session_state.current_kode_unik != st.session_state.kode_unik_input):
            _update_student_info_callback(student_df)

        with col_siswa_2:
            st.text_input("Nama Siswa", value=st.session_state.found_nama_siswa, disabled=True, key="nama_siswa_output")

        # --- Bagian Detail Pembayaran (Tabel Dinamis) ---
        st.header("2. Detail Pembayaran")

        def add_item_row():
            st.session_state.payment_items.append({'jenis': 'SPP', 'bulan_ujian': '', 'jumlah': 0, 'diskon': 0})
            st.session_state.item_keys_counter += 1

        def delete_item_row(index_to_delete):
            if len(st.session_state.payment_items) > index_to_delete:
                st.session_state.payment_items.pop(index_to_delete)
            st.session_state.item_keys_counter += 1

        st.button("➕ Tambah Item Pembayaran", on_click=add_item_row)

        total_jumlah_item = 0
        total_diskon_item = 0

        if st.session_state.payment_items:
            st.subheader("Daftar Item Pembayaran")

            for i, item in enumerate(st.session_state.payment_items):
                st.markdown(f"**Item {i+1}**")
                cols_item = st.columns([2, 2, 2, 2, 1])

                with cols_item[0]:
                    item['jenis'] = st.selectbox(
                        f"Jenis Pembayaran",
                        ['SPP', 'UTS', 'UAS'],
                        index=['SPP', 'UTS', 'UAS'].index(item['jenis']),
                        key=f"jenis_item_{i}_{st.session_state.item_keys_counter}"
                    )
                with cols_item[1]:
                    item['bulan_ujian'] = st.text_input(
                        f"Bulan/Ujian",
                        value=item['bulan_ujian'],
                        key=f"bulan_ujian_item_{i}_{st.session_state.item_keys_counter}"
                    )
                with cols_item[2]:
                    item['jumlah'] = st.number_input(
                        f"Jumlah (Rp)",
                        min_value=0, value=item['jumlah'], step=1000,
                        key=f"jumlah_item_{i}_{st.session_state.item_keys_counter}"
                    )
                with cols_item[3]:
                    item['diskon'] = st.number_input(
                        f"Diskon (Rp)",
                        min_value=0, value=item['diskon'], step=1000,
                        key=f"diskon_item_{i}_{st.session_state.item_keys_counter}"
                    )
                with cols_item[4]:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.button("🗑️ Hapus", on_click=delete_item_row, args=(i,), key=f"delete_item_btn_{i}_{st.session_state.item_keys_counter}")
                st.markdown("---")

                total_jumlah_item += item['jumlah']
                total_diskon_item += item['diskon']
        else:
            st.info("Belum ada item pembayaran ditambahkan.")

        # --- Ringkasan Pembayaran ---
        grandtotal = total_jumlah_item - total_diskon_item
        st.header("3. Ringkasan Pembayaran")
        st.write(f"**Subtotal:** Rp {total_jumlah_item:,.0f}")
        st.write(f"**Total Diskon:** Rp {total_diskon_item:,.0f}")
        st.markdown(f"## **GRANDTOTAL: Rp {grandtotal:,.0f}**")

        # --- Jenis Pembayaran ---
        st.header("4. Metode Pembayaran")
        jenis_pembayaran_final = st.selectbox("Pilih Metode Pembayaran", ["Tunai", "Transfer Bank", "Lainnya"], key="metode_pembayaran_final")

        # --- Tombol Simpan ---
        st.markdown("---")
        # Tombol simpan ditampilkan di sini, tidak disabled lagi karena kwitansi ditampilkan setelah rerun
        if st.button("💾 Simpan Pembayaran", type="primary"):
            current_kode_unik = st.session_state.current_kode_unik
            current_nama_siswa = st.session_state.found_nama_siswa

            if not current_kode_unik or not current_nama_siswa:
                st.error("Silakan masukkan Kode Unik Siswa yang valid.")
                return
            if not st.session_state.payment_items:
                st.error("Silakan tambahkan setidaknya satu item pembayaran.")
                return

            payment_id = st.session_state.payment_id_display
            payment_date = st.session_state.payment_date_input
            optional_notes = st.session_state.optional_notes_input

            receipt_items = []
            for item in st.session_state.payment_items:
                payment_record = {
                    'Nomor Pembayaran': payment_id,
                    'Tanggal': payment_date.strftime('%Y-%m-%d'),
                    'Kode Unik Siswa': current_kode_unik,
                    'Nama Siswa': current_nama_siswa,
                    'Jenis Pembayaran': item['jenis'],
                    'Bulan/Ujian': item['bulan_ujian'],
                    'Jumlah': item['jumlah'],
                    'Diskon': item['diskon'],
                    'Grandtotal': item['jumlah'] - item['diskon']
                }
                receipt_items.append({
                    'jenis': item['jenis'],
                    'bulan_ujian': item['bulan_ujian'],
                    'jumlah': item['jumlah'],
                    'diskon': item['diskon'],
                    'subtotal_item': item['jumlah'] - item['diskon']
                })

                if item['jenis'] == 'SPP':
                    spp_df = load_payment_data(SPP_DATA_PATH)
                    spp_df = pd.concat([spp_df, pd.DataFrame([payment_record])], ignore_index=True)
                    save_payment_data(spp_df, SPP_DATA_PATH)
                elif item['jenis'] == 'UTS':
                    uts_df = load_payment_data(UTS_DATA_PATH)
                    uts_df = pd.concat([uts_df, pd.DataFrame([payment_record])], ignore_index=True)
                    save_payment_data(uts_df, UTS_DATA_PATH)
                elif item['jenis'] == 'UAS':
                    uas_df = load_payment_data(UAS_DATA_PATH)
                    uas_df = pd.concat([uas_df, pd.DataFrame([payment_record])], ignore_index=True)
                    save_payment_data(uas_df, UAS_DATA_PATH)

            st.success("Pembayaran berhasil dicatat!")

            # Simpan semua data yang diperlukan untuk kwitansi ke session state
            st.session_state.receipt_data = {
                'payment_id': payment_id,
                'payment_date': payment_date,
                'current_nama_siswa': current_nama_siswa,
                'current_kode_unik': current_kode_unik,
                'optional_notes': optional_notes,
                'receipt_items': receipt_items,
                'total_jumlah_item': total_jumlah_item,
                'total_diskon_item': total_diskon_item,
                'grandtotal': grandtotal,
                'jenis_pembayaran_final': jenis_pembayaran_final
            }

            # Generate PDF kwitansi dan simpan path-nya
            pdf_file_path = generate_receipt_pdf(st.session_state.receipt_data)
            if pdf_file_path:
                st.session_state.receipt_data['pdf_path'] = pdf_file_path
            else:
                st.session_state.receipt_data['pdf_path'] = None # Jika gagal

            st.session_state.show_receipt = True # Set flag untuk menampilkan kwitansi
            st.rerun() # Trigger rerun untuk menampilkan kwitansi dan menyembunyikan form

    # --- Tampilkan Kwitansi (Conditional) ---
    if st.session_state.show_receipt:
        receipt_data = st.session_state.receipt_data
        st.subheader("Kwitansi Pembayaran")
        st.write("---")
        st.write(f"**YAYASAN FATHAN MUBINA**")
        st.write(f"Nomor Pembayaran: **{receipt_data['payment_id']}**")
        st.write(f"Tanggal: **{receipt_data['payment_date'].strftime('%d %B %Y')}**")
        st.write(f"Siswa: **{receipt_data['current_nama_siswa']}** (Kode Unik: {receipt_data['current_kode_unik']})")
        if receipt_data['optional_notes']:
            st.write(f"Keterangan: {receipt_data['optional_notes']}")
        st.write("---")
        st.write("**DETAIL PEMBAYARAN:**")
        for item in receipt_data['receipt_items']:
            st.write(f"- {item['jenis']} ({item['bulan_ujian']}): Rp {item['jumlah']:,.0f} (Diskon: Rp {item['diskon']:,.0f}) -> **Rp {item['subtotal_item']:,.0f}**")
        st.write("---")
        st.write(f"Subtotal: Rp {receipt_data['total_jumlah_item']:,.0f}")
        st.write(f"Diskon Total: Rp {receipt_data['total_diskon_item']:,.0f}")
        st.markdown(f"### **GRANDTOTAL: Rp {receipt_data['grandtotal']:,.0f}**")
        st.write(f"Metode Pembayaran: {receipt_data['jenis_pembayaran_final']}")
        st.write("---")
        st.write("Terima kasih atas kepercayaan Anda!")
        st.write("*(Ini adalah preview kwitansi. Untuk cetak, Anda bisa mengimplementasikan PDF generation, atau fitur cetak browser)*")

        # Tombol Download Kwitansi
        if receipt_data.get('pdf_path') and os.path.exists(receipt_data['pdf_path']):
            with open(receipt_data['pdf_path'], "rb") as pdf_file:
                st.download_button(
                    label="⬇️ Unduh Kwitansi PDF",
                    data=pdf_file,
                    file_name=os.path.basename(receipt_data['pdf_path']),
                    mime="application/pdf",
                    type="secondary"
                )
            st.info(f"Kwitansi juga disimpan secara otomatis di folder: `pages/kwitansi_pembayaran/{os.path.basename(receipt_data['pdf_path'])}`")
        else:
            st.error("File kwitansi PDF tidak dapat ditemukan atau dibuat.")


        # Tombol untuk kembali ke form setelah melihat kwitansi
        st.markdown("---") # Garis pemisah
        if st.button("🔄 Kembali ke Formulir Baru"):
            reset_form_state()
            st.rerun() # Kembali ke form kosong

    # --- Tombol Reset Formulir (Opsional, jika ingin selalu ada) ---
    # Jika Anda ingin tombol reset selalu ada terlepas dari tampilan kwitansi/form:
    # st.markdown("---")
    # if st.button("🔄 Reset Formulir", help="Menghapus semua input di formulir ini."):
    #     reset_form_state()
    #     st.rerun()


def reset_form_state():
    """Meriset semua session state terkait formulir pembayaran dan tampilan kwitansi."""
    st.session_state.payment_items = []
    st.session_state.kode_unik_input = ""
    st.session_state.payment_id = f"TRX-{uuid.uuid4().hex[:8].upper()}"
    st.session_state.payment_date = datetime.now().date()
    st.session_state.optional_notes = ""
    st.session_state.found_nama_siswa = ""
    st.session_state.current_kode_unik = ""
    st.session_state.item_keys_counter = 0
    # Reset state kwitansi
    st.session_state.show_receipt = False
    st.session_state.receipt_data = {} # Penting untuk mengosongkan data kwitansi
    st.cache_data.clear()

# --- Panggil Fungsi Utama ---
if __name__ == '__main__':
    show_payment_form()