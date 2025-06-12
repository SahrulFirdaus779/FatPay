import streamlit as st
import pandas as pd
import datetime
import os
import subprocess
import urllib.parse

# File CSV khusus untuk pembayaran UTS
FILE_PATH = "uts_data.csv"
PAYMENT_TYPE = "UTS" # Definisikan jenis pembayaran di sini

# Fungsi untuk membaca data dari CSV
def load_data():
    columns = ["NIS", "Nama", "Bulan/Ujian", "Jumlah", "No Orang Tua", "Tanggal"]
    if os.path.exists(FILE_PATH):
        try:
            df = pd.read_csv(FILE_PATH)
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            return df[columns]
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# Fungsi untuk menyimpan data baru ke CSV
def save_data(nis, nama, bulan_atau_ujian_list, jumlah, no_hp):
    df = load_data()
    bulan_atau_ujian_str = ", ".join(bulan_atau_ujian_list)
    tanggal_pembayaran = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    new_data = pd.DataFrame([[nis, nama, bulan_atau_ujian_str, jumlah, no_hp, tanggal_pembayaran]],
                            columns=["NIS", "Nama", "Bulan/Ujian", "Jumlah", "No Orang Tua", "Tanggal"])
    
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(FILE_PATH, index=False)
    return tanggal_pembayaran

# Fungsi untuk mengirim pesan WhatsApp
def send_whatsapp_message(no_hp, nama, bulan_atau_ujian_list, jumlah, tanggal):
    pesan = (
        f'Kepada Yth. Orangtua Ananda *{nama}* Ditempat.\n\n'
        f"Kami menginformasikan bahwa pada *{tanggal}* ananda *{nama}* telah melakukan pembayaran {PAYMENT_TYPE} untuk ujian *{', '.join(bulan_atau_ujian_list)}* dengan nominal sebesar *Rp{jumlah:,.0f}*.\n\n"
        f"Atas perhatiannya kami mengucapkan Terima kasih! 🙏"
    )
    pesan_encoded = urllib.parse.quote_plus(pesan)
    wa_link = f"https://wa.me/62{no_hp}?text={pesan_encoded}"

    try:
        if os.name == "nt":  # Windows
            subprocess.Popen(f'start "" "{wa_link}"', shell=True)
        elif os.name == "posix":  # Linux/MacOS
            subprocess.run(["xdg-open", wa_link])
        st.success("✅ Pesan WhatsApp berhasil dikirim ke WhatsApp Desktop!")
    except Exception as e:
        st.error(f"❌ Gagal mengirim WhatsApp: {e}")

st.title(f"👨‍💻 Pembayaran {PAYMENT_TYPE}")

# Input Form Pembayaran
nis = st.text_input("📌 NIS Siswa", key=f"{PAYMENT_TYPE.lower()}_nis")
nama = st.text_input("📌 Nama Siswa", key=f"{PAYMENT_TYPE.lower()}_nama")
ujian_uts = st.multiselect("📌 Pilih Ujian UTS", ["UTS Ganjil", "UTS Genap"], key=f"{PAYMENT_TYPE.lower()}_ujian")
jumlah = st.number_input("📌 Jumlah Pembayaran (Rp)", min_value=0, step=10000, key=f"{PAYMENT_TYPE.lower()}_jumlah")
no_hp = st.text_input("📌 Nomor WhatsApp Orang Tua (Tanpa +62)", value="89527509633", key=f"{PAYMENT_TYPE.lower()}_no_hp")

if st.button(f"💾 Simpan & Kirim Notifikasi {PAYMENT_TYPE}", key=f"{PAYMENT_TYPE.lower()}_submit"):
    if nis and nama and ujian_uts and jumlah > 0 and no_hp:
        tanggal_pembayaran = save_data(nis, nama, ujian_uts, jumlah, no_hp)
        send_whatsapp_message(no_hp, nama, ujian_uts, jumlah, tanggal_pembayaran)
        st.success(f"✅ Pembayaran {PAYMENT_TYPE} {nama} untuk ujian {', '.join(ujian_uts)} berhasil dicatat & notifikasi terkirim.")
        st.rerun()
    else:
        st.warning(f"⚠️ Harap isi semua data untuk pembayaran {PAYMENT_TYPE}!")

# Tampilkan data pembayaran UTS
st.subheader(f"📊 Riwayat Pembayaran {PAYMENT_TYPE}")
df = load_data() 

if not df.empty:
    df.index = range(len(df))
    st.dataframe(df)

    # Inisialisasi session state untuk data yang diedit
    if 'selected_edit_row_data_uts' not in st.session_state:
        st.session_state.selected_edit_row_data_uts = None
    if 'selected_index_uts' not in st.session_state: # New: Store original index
        st.session_state.selected_index_uts = -1

    row_labels = [f"{row['Nama']} - {row['Bulan/Ujian']} - Rp{row['Jumlah']} ({row['Tanggal']})" for idx, row in df.iterrows()]
    selected_label = st.selectbox(f"📌 Pilih Data {PAYMENT_TYPE} untuk Diedit / Dihapus", options=row_labels, key=f"{PAYMENT_TYPE.lower()}_select_edit_delete")

    # This button triggers the display of the edit form
    if st.button(f"📝 Edit Data {PAYMENT_TYPE}", key=f"{PAYMENT_TYPE.lower()}_edit_button"):
        if selected_label:
            # Find the index in the currently displayed DataFrame (df)
            selected_index_df_display = df[df.apply(lambda row: f"{row['Nama']} - {row['Bulan/Ujian']} - Rp{row['Jumlah']} ({row['Tanggal']})" == selected_label, axis=1)].index[0]
            st.session_state.selected_edit_row_data_uts = df.loc[selected_index_df_display].to_dict()
            st.session_state.selected_index_uts = selected_index_df_display # Store the actual index
            st.rerun() # Rerun to display the form with pre-filled data
        else:
            st.warning("⚠️ Harap pilih data yang akan diedit terlebih dahulu!")

    # Tampilkan formulir edit jika data baris yang dipilih ada di session_state
    if st.session_state.selected_edit_row_data_uts:
        row_to_edit = st.session_state.selected_edit_row_data_uts
        original_index_for_edit = st.session_state.selected_index_uts

        with st.form(f"edit_form_{PAYMENT_TYPE.lower()}"): # Key for the form
            st.markdown(f"**Edit Data {row_to_edit.get('Nama', '')}**")
            edit_nis = st.text_input("📌 Edit NIS", row_to_edit["NIS"], key=f"edit_nis_{PAYMENT_TYPE.lower()}")
            edit_nama = st.text_input("📌 Edit Nama", row_to_edit["Nama"], key=f"edit_nama_{PAYMENT_TYPE.lower()}")
            edit_ujian_uts = st.text_input("📌 Edit Ujian (pisahkan dengan koma jika lebih dari satu)", row_to_edit["Bulan/Ujian"], key=f"edit_ujian_{PAYMENT_TYPE.lower()}")
            edit_jumlah = st.number_input("📌 Edit Jumlah Pembayaran (Rp)", value=row_to_edit["Jumlah"], step=10000, key=f"edit_jumlah_{PAYMENT_TYPE.lower()}")
            edit_no_hp = st.text_input("📌 Edit Nomor WA", row_to_edit["No Orang Tua"], key=f"edit_no_hp_{PAYMENT_TYPE.lower()}")
            submitted = st.form_submit_button(f"💾 Simpan Perubahan {PAYMENT_TYPE}") 
            
            if submitted:
                current_df_for_update = load_data() # Reload data to get the absolute latest state
                
                # Check if the original index still exists in the current DataFrame
                if original_index_for_edit in current_df_for_update.index:
                    current_df_for_update.loc[original_index_for_edit, ["NIS", "Nama", "Bulan/Ujian", "Jumlah", "No Orang Tua"]] = \
                        edit_nis, edit_nama, edit_ujian_uts, edit_jumlah, edit_no_hp
                    
                    current_df_for_update.to_csv(FILE_PATH, index=False)
                    st.success(f"✅ Data {PAYMENT_TYPE} berhasil diperbarui!")
                    st.session_state.selected_edit_row_data_uts = None # Clear selected data after successful edit
                    st.session_state.selected_index_uts = -1 # Clear original index
                    st.rerun()
                else:
                    st.error("❌ Data yang akan diedit tidak ditemukan di data terbaru. Mungkin sudah dihapus atau diubah secara eksternal.")
        st.markdown("---") # Garis pemisah setelah form edit
    
    # Hapus Data Button (independent of edit form submission)
    if st.button(f"🗑️ Hapus Data {PAYMENT_TYPE}", key=f"{PAYMENT_TYPE.lower()}_delete_button"):
        if selected_label: # Ensure a row is selected
            current_df_for_delete = load_data() # Reload data for deletion to ensure latest state
            
            # Find the index of the selected item in the current DataFrame (important for consistency)
            selected_index_current_df = df[df.apply(lambda row: f"{row['Nama']} - {row['Bulan/Ujian']} - Rp{row['Jumlah']} ({row['Tanggal']})" == selected_label, axis=1)].index[0]
            
            # Check if the index to delete still exists
            if selected_index_current_df in current_df_for_delete.index:
                current_df_for_delete.drop(selected_index_current_df, inplace=True)
                current_df_for_delete.to_csv(FILE_PATH, index=False)
                st.warning(f"🗑️ Data {PAYMENT_TYPE} berhasil dihapus!")
                st.session_state.selected_edit_row_data_uts = None # Clear selected data after successful deletion
                st.session_state.selected_index_uts = -1
                st.rerun()
            else:
                st.error("❌ Data tidak ditemukan untuk dihapus. Mungkin sudah dihapus oleh pengguna lain.")
        else:
            st.warning("⚠️ Harap pilih data yang akan dihapus terlebih dahulu!")

else:
    st.warning(f"📢 Belum ada data pembayaran {PAYMENT_TYPE} yang tercatat!")
