import streamlit as st
import pandas as pd
import os

# Jalur file CSV untuk setiap jenis pembayaran
FILE_PATHS = {
    "SPP": "spp_data.csv",
    "UTS": "uts_data.csv",
    "UAS": "uas_data.csv"
}

# Fungsi untuk membaca data dari CSV tertentu
def load_single_data(file_path):
    # Kolom standar yang diharapkan untuk setiap file pembayaran
    columns = ["NIS", "Nama", "Bulan/Ujian", "Jumlah", "No Orang Tua", "Tanggal"]
    
    if os.path.exists(file_path):
        try:
            # Coba baca file CSV
            df = pd.read_csv(file_path)
            # Pastikan DataFrame memiliki kolom yang diharapkan, tambahkan jika hilang
            for col in columns:
                if col not in df.columns:
                    df[col] = None # Tambahkan kolom yang hilang dengan nilai None
            return df[columns] # Kembalikan DataFrame dengan urutan kolom yang benar
        except pd.errors.EmptyDataError:
            # Jika file kosong atau hanya header kosong, kembalikan DataFrame kosong dengan kolom yang benar
            return pd.DataFrame(columns=columns)
    # Jika file tidak ada, kembalikan DataFrame kosong dengan kolom yang benar
    return pd.DataFrame(columns=columns)

# Fungsi untuk memuat semua data pembayaran
def load_all_data():
    # Kolom untuk DataFrame gabungan
    all_columns = ["NIS", "Nama", "Jenis Pembayaran", "Bulan/Ujian", "Jumlah", "No Orang Tua", "Tanggal"]
    all_data = pd.DataFrame(columns=all_columns)
    
    for jenis_pembayaran, path in FILE_PATHS.items():
        df_temp = load_single_data(path)
        if not df_temp.empty:
            df_temp["Jenis Pembayaran"] = jenis_pembayaran # Tambahkan kolom Jenis Pembayaran
            # Pastikan semua kolom yang diperlukan ada sebelum concat
            for col in all_columns:
                if col not in df_temp.columns:
                    df_temp[col] = None
            all_data = pd.concat([all_data, df_temp[all_columns]], ignore_index=True)
            
    return all_data

st.title("📊 Dashboard FatPay")
st.write("Selamat datang di Dashboard FatPay! Berikut adalah ringkasan pembayaran dari seluruh jenis pembayaran.")

# Memuat semua data
df_all = load_all_data()

if not df_all.empty:
    st.subheader("Ringkasan Data Pembayaran Keseluruhan")
    st.dataframe(df_all)

    # Contoh agregasi data
    total_pembayaran = df_all["Jumlah"].sum()
    st.metric(label="Total Seluruh Pembayaran", value=f"Rp {total_pembayaran:,.0f}")

    # Agregasi berdasarkan jenis pembayaran
    st.subheader("Total Pembayaran per Jenis")
    pembayaran_per_jenis = df_all.groupby("Jenis Pembayaran")["Jumlah"].sum().reset_index()
    st.dataframe(pembayaran_per_jenis)

    # Anda bisa menambahkan grafik atau visualisasi lain di sini
    st.subheader("Distribusi Pembayaran per Jenis")
    st.bar_chart(pembayaran_per_jenis.set_index("Jenis Pembayaran"))

    # Agregasi total siswa per jenis pembayaran
    st.subheader("Jumlah Pembayaran Unik per Jenis")
    unique_payments_per_type = df_all.groupby("Jenis Pembayaran")["NIS"].nunique().reset_index()
    unique_payments_per_type.columns = ["Jenis Pembayaran", "Jumlah Pembayaran Unik (NIS)"]
    st.dataframe(unique_payments_per_type)

else:
    st.info("Belum ada data pembayaran yang tercatat di semua jenis.")

st.markdown("---")
st.write("Gunakan sidebar di kiri untuk menavigasi ke halaman pembayaran tertentu.")
