import streamlit as st
import pandas as pd
import datetime
import os
import subprocess
import urllib.parse  # Untuk encoding pesan dengan benar

# File CSV untuk menyimpan riwayat pembayaran
FILE_PATH = "data_pembayaran.csv"

# Fungsi untuk membaca data dari CSV
def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    return pd.DataFrame(columns=["NIS", "Nama", "Bulan", "Jumlah", "No Orang Tua", "Tanggal"])

# Fungsi untuk menyimpan data baru ke CSV
def save_data(nis, nama, bulan_list, jumlah, no_hp):
    df = load_data()
    bulan_str = ", ".join(bulan_list)
    tanggal_pembayaran = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")  # Tambahkan tanggal pembayaran
    new_data = pd.DataFrame([[nis, nama, bulan_str, jumlah, no_hp, tanggal_pembayaran]],
                            columns=["NIS", "Nama", "Bulan", "Jumlah", "No Orang Tua", "Tanggal"])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(FILE_PATH, index=False)
    return tanggal_pembayaran  # Mengembalikan tanggal pembayaran

# Fungsi untuk mengirim pesan WhatsApp ke WhatsApp Desktop
def send_whatsapp_message(no_hp, nama, bulan_list, jumlah, tanggal):
    pesan = (
        f'Kepada YTh Orangtua Ananda *{nama}* Ditempat.\n \n'
        
        f"Kami menginformasikan bahwa pada *{tanggal}* ananda *{nama}* telah melakukan pembayaran SPP untuk bulan *{', '.join(bulan_list)}* dengan nominal sebesar *Rp{jumlah}*\n\n"
        f"Atas perhatiannya kami mengucapkan Terima kasih! 🙏"
    )
    pesan_encoded = urllib.parse.quote_plus(pesan)  # Encoding pesan agar URL valid
    wa_link = f"https://wa.me/62{no_hp}?text={pesan_encoded}"  # Format URL WhatsApp Web/Desktop yang lebih kompatibel

    try:
        if os.name == "nt":  # Windows
            subprocess.run(["cmd", "/c", "start", wa_link], shell=True)
        elif os.name == "posix":  # Linux/MacOS
            subprocess.run(["xdg-open", wa_link])
        st.success("✅ Pesan WhatsApp berhasil dikirim ke WhatsApp Desktop!")
    except Exception as e:
        st.error(f"❌ Gagal mengirim WhatsApp: {e}")

# Tampilan Streamlit
st.title("📌 FatPay")

# Input Form Pembayaran
nis = st.text_input("📌 NIS Siswa")
nama = st.text_input("📌 Nama Siswa")
bulan = st.multiselect("📌 Pilih Bulan Pembayaran", 
                        ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                         "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
jumlah = st.number_input("📌 Jumlah Pembayaran (Rp)", min_value=0, step=10000)
no_hp = st.text_input("📌 Nomor WhatsApp Orang Tua (Tanpa +62)", value="89527509633")  # WA kamu

if st.button("💾 Simpan & Kirim Notifikasi"):
    if nis and nama and bulan and jumlah > 0 and no_hp:
        tanggal_pembayaran = save_data(nis, nama, bulan, jumlah, no_hp)  # Simpan data dan ambil tanggal pembayaran
        send_whatsapp_message(no_hp, nama, bulan, jumlah, tanggal_pembayaran)  # Kirim pesan dengan tanggal pembayaran
        st.success(f"✅ Pembayaran {nama} untuk bulan {', '.join(bulan)} berhasil dicatat & notifikasi terkirim.")
        st.rerun()
    else:
        st.warning("⚠️ Harap isi semua data!")

# Tampilkan data pembayaran
st.subheader("📊 Riwayat Pembayaran")
df = load_data()
if not df.empty:
    df.index = range(len(df))  # Reset index
    st.dataframe(df)

    # **Fitur Edit & Hapus Data**
    # Buat label deskriptif untuk setiap entri
    row_labels = [f"{row['Nama']} - {row['Bulan']} - Rp{row['Jumlah']}" for idx, row in df.iterrows()]
    selected_label = st.selectbox("📌 Pilih Data untuk Diedit / Dihapus", options=row_labels)

    # Temukan index dari data yang dipilih
    selected_index = row_labels.index(selected_label)

    
    if st.button("📝 Edit Data"):
        with st.form("edit_form"):
            edit_nis = st.text_input("📌 Edit NIS", df.loc[selected_index, "NIS"])
            edit_nama = st.text_input("📌 Edit Nama", df.loc[selected_index, "Nama"])
            edit_bulan = st.text_input("📌 Edit Bulan", df.loc[selected_index, "Bulan"])
            edit_jumlah = st.number_input("📌 Edit Jumlah Pembayaran (Rp)", value=df.loc[selected_index, "Jumlah"], step=10000)
            edit_no_hp = st.text_input("📌 Edit Nomor WA", df.loc[selected_index, "No Orang Tua"])
            submitted = st.form_submit_button("💾 Simpan Perubahan")
            
            if submitted:
                df.loc[selected_index, ["NIS", "Nama", "Bulan", "Jumlah", "No Orang Tua"]] = edit_nis, edit_nama, edit_bulan, edit_jumlah, edit_no_hp
                df.to_csv(FILE_PATH, index=False)
                st.success("✅ Data berhasil diperbarui!")
                st.rerun()

    if st.button("🗑️ Hapus Data"):
        df.drop(selected_index, inplace=True)
        df.to_csv(FILE_PATH, index=False)
        st.warning("🗑️ Data berhasil dihapus!")
        st.rerun()
else:
    st.warning("📢 Belum ada data pembayaran yang tercatat!")
