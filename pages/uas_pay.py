import streamlit as st
import pandas as pd
import datetime
import os
import subprocess
import urllib.parse

# File CSV khusus untuk pembayaran UAS
FILE_PATH = "uas_data.csv"
PAYMENT_TYPE = "UAS" # Definisikan jenis pembayaran di sini

# Fungsi untuk membaca data dari CSV
def load_data():
    columns = ["NIS", "Nama", "Bulan/Ujian", "Jumlah", "No Orang Tua", "Tanggal"]
    if os.path.exists(FILE_PATH):
        try:
            df = pd.read_csv(FILE_PATH)
            for col in columns:
                if col not in df.columns:
                    df[col] = None 
            return df[columns] # Kembalikan DataFrame dengan urutan kolom yang benar
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

st.title(f"🎓 Pembayaran {PAYMENT_TYPE}")

# Input Form Pembayaran
nis = st.text_input("📌 NIS Siswa", key=f"{PAYMENT_TYPE.lower()}_nis")
nama = st.text_input("📌 Nama Siswa", key=f"{PAYMENT_TYPE.lower()}_nama")
ujian_uas = st.multiselect("📌 Pilih Ujian UAS", ["UAS Ganjil", "UAS Genap"], key=f"{PAYMENT_TYPE.lower()}_ujian")
jumlah = st.number_input("📌 Jumlah Pembayaran (Rp)", min_value=0, step=10000, key=f"{PAYMENT_TYPE.lower()}_jumlah")
no_hp = st.text_input("📌 Nomor WhatsApp Orang Tua (Tanpa +62)", value="89527509633", key=f"{PAYMENT_TYPE.lower()}_no_hp")

if st.button(f"💾 Simpan & Kirim Notifikasi {PAYMENT_TYPE}", key=f"{PAYMENT_TYPE.lower()}_submit"):
    if nis and nama and ujian_uas and jumlah > 0 and no_hp:
        tanggal_pembayaran = save_data(nis, nama, ujian_uas, jumlah, no_hp)
        send_whatsapp_message(no_hp, nama, ujian_uas, jumlah, tanggal_pembayaran)
        st.success(f"✅ Pembayaran {PAYMENT_TYPE} {nama} untuk ujian {', '.join(ujian_uas)} berhasil dicatat & notifikasi terkirim.")
        st.rerun()
    else:
        st.warning(f"⚠️ Harap isi semua data untuk pembayaran {PAYMENT_TYPE}!")

# Tampilkan data pembayaran UAS
st.subheader(f"📊 Riwayat Pembayaran {PAYMENT_TYPE}")
df = load_data() 

if not df.empty:
    df.index = range(len(df))
    st.dataframe(df)

    # Buat label deskriptif untuk setiap entri, termasuk Tanggal
    row_labels = [f"{row['Nama']} - {row['Bulan/Ujian']} - Rp{row['Jumlah']} ({row['Tanggal']})" for idx, row in df.iterrows()]
    selected_label = st.selectbox(f"📌 Pilih Data {PAYMENT_TYPE} untuk Diedit / Dihapus", options=row_labels, key=f"{PAYMENT_TYPE.lower()}_select_edit_delete")

    # Temukan indeks dari data yang dipilih di DataFrame saat ini
    # Ini harus dilakukan setiap kali untuk memastikan indeks selalu benar
    # meskipun df di-rerun atau data berubah
    if selected_label: # Pastikan ada label yang dipilih
        selected_index_current_df = df[df.apply(lambda row: f"{row['Nama']} - {row['Bulan/Ujian']} - Rp{row['Jumlah']} ({row['Tanggal']})" == selected_label, axis=1)].index[0]
        # Data yang dipilih dari DataFrame yang ditampilkan
        selected_row_data = df.loc[selected_index_current_df].to_dict()

        if st.button(f"📝 Edit Data {PAYMENT_TYPE}", key=f"{PAYMENT_TYPE.lower()}_edit_button"):
            # Gunakan st.session_state untuk menyimpan data baris yang dipilih
            # Ini diperlukan karena Streamlit me-rerun script setelah setiap interaksi
            st.session_state[f'edit_selected_row_data_{PAYMENT_TYPE.lower()}'] = selected_row_data
            st.session_state[f'edit_selected_index_{PAYMENT_TYPE.lower()}'] = selected_index_current_df # Simpan indeks asli

            # Pemicu rerun agar form edit muncul dengan nilai pre-filled
            st.rerun()

        # Tampilkan formulir edit jika data baris yang dipilih ada di session_state
        if f'edit_selected_row_data_{PAYMENT_TYPE.lower()}' in st.session_state and \
           st.session_state[f'edit_selected_row_data_{PAYMENT_TYPE.lower()}'] is not None:
            
            row_to_edit = st.session_state[f'edit_selected_row_data_{PAYMENT_TYPE.lower()}']
            original_index_for_edit = st.session_state[f'edit_selected_index_{PAYMENT_TYPE.lower()}']

            with st.form(f"edit_form_{PAYMENT_TYPE.lower()}"):
                edit_nis = st.text_input("📌 Edit NIS", row_to_edit["NIS"], key=f"edit_nis_{PAYMENT_TYPE.lower()}")
                edit_nama = st.text_input("📌 Edit Nama", row_to_edit["Nama"], key=f"edit_nama_{PAYMENT_TYPE.lower()}")
                edit_bulan_ujian = st.text_input("📌 Edit Ujian (pisahkan dengan koma jika lebih dari satu)", row_to_edit["Bulan/Ujian"], key=f"edit_ujian_{PAYMENT_TYPE.lower()}")
                edit_jumlah = st.number_input("📌 Edit Jumlah Pembayaran (Rp)", value=row_to_edit["Jumlah"], step=10000, key=f"edit_jumlah_{PAYMENT_TYPE.lower()}")
                edit_no_hp = st.text_input("📌 Edit Nomor WA", row_to_edit["No Orang Tua"], key=f"edit_no_hp_{PAYMENT_TYPE.lower()}")
                submitted = st.form_submit_button(f"💾 Simpan Perubahan {PAYMENT_TYPE}") 
                
                if submitted:
                    current_df_for_update = load_data() # Muat ulang data terbaru dari CSV

                    # Pastikan indeks yang akan diedit masih valid di DataFrame terbaru
                    if original_index_for_edit in current_df_for_update.index:
                        current_df_for_update.loc[original_index_for_edit, ["NIS", "Nama", "Bulan/Ujian", "Jumlah", "No Orang Tua"]] = \
                            edit_nis, edit_nama, edit_bulan_ujian, edit_jumlah, edit_no_hp
                        
                        current_df_for_update.to_csv(FILE_PATH, index=False)
                        st.success(f"✅ Data {PAYMENT_TYPE} berhasil diperbarui!")
                        # Hapus data yang disimpan di session state setelah perubahan berhasil
                        st.session_state[f'edit_selected_row_data_{PAYMENT_TYPE.lower()}'] = None
                        st.session_state[f'edit_selected_index_{PAYMENT_TYPE.lower()}'] = -1
                        st.rerun()
                    else:
                        st.error("❌ Data yang akan diedit tidak ditemukan di data terbaru. Mungkin sudah dihapus atau diubah secara eksternal.")
            st.markdown("---") # Garis pemisah setelah form edit
    
        if st.button(f"🗑️ Hapus Data {PAYMENT_TYPE}", key=f"{PAYMENT_TYPE.lower()}_delete_button"):
            # Muat ulang data terbaru dari CSV
            current_df_for_delete = load_data()
            
            # Gunakan indeks yang dipilih dari selectbox untuk menghapus
            # Pastikan indeks yang akan dihapus masih valid di DataFrame terbaru
            if selected_index_current_df in current_df_for_delete.index:
                current_df_for_delete.drop(selected_index_current_df, inplace=True)
                current_df_for_delete.to_csv(FILE_PATH, index=False)
                st.warning(f"🗑️ Data {PAYMENT_TYPE} berhasil dihapus!")
                # Hapus data yang disimpan di session state setelah penghapusan berhasil
                st.session_state[f'edit_selected_row_data_{PAYMENT_TYPE.lower()}'] = None
                st.session_state[f'edit_selected_index_{PAYMENT_TYPE.lower()}'] = -1
                st.rerun()
            else:
                st.error("❌ Data tidak ditemukan untuk dihapus. Mungkin sudah dihapus oleh pengguna lain.")
else:
    st.warning(f"📢 Belum ada data pembayaran {PAYMENT_TYPE} yang tercatat!")
