import streamlit as st
import pandas as pd
from datetime import datetime

# Asumsi lokasi file ini adalah di folder 'pages'
# Jika tidak, sesuaikan path ini agar sesuai dengan struktur proyek Anda
SPP_DATA_PATH = 'spp_data.csv'
UTS_DATA_PATH = 'uts_data.csv' # Tambahkan jika halaman ini juga mengelola UTS/UAS
UAS_DATA_PATH = 'uas_data.csv' # Tambahkan jika halaman ini juga mengelola UTS/UAS

@st.cache_data
def load_data(file_path):
    """
    Memuat data dari CSV, mengembalikan DataFrame kosong jika file tidak ditemukan.
    Mengisi NaN di kolom numerik dengan 0 dan mengkonversinya ke int.
    Memastikan kolom Tanggal diformat dengan benar dan mengganti NaT dengan string kosong.
    """
    # Kolom default harus sesuai dengan apa yang disimpan oleh payment_form.py
    # Tanpa 'Nomor WhatsApp Orang Tua'
    default_columns_for_empty_df = [
        'Nomor Pembayaran', 'Tanggal', 'Kode Unik Siswa', 'Nama Siswa',
        'Jenis Pembayaran', 'Bulan/Ujian', 'Jumlah', 'Diskon', 'Grandtotal'
    ]
    try:
        df = pd.read_csv(file_path)

        if 'Tanggal' in df.columns:
            # Konversi ke datetime, paksa error menjadi NaT
            df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
            # Ganti NaT (dari coerce) dengan string kosong setelah format
            df['Tanggal'] = df['Tanggal'].dt.strftime('%Y-%m-%d').fillna('') # Ini memastikan 'None' diubah jadi string kosong
            
        # PERBAIKAN UNTUK MENGATASI ValueError: cannot convert float NaN to integer
        # Mengisi nilai NaN di kolom 'Jumlah', 'Diskon', dan 'Grandtotal' dengan 0
        # Lalu mengkonversi kolom tersebut ke tipe integer.
        numeric_cols = ['Jumlah', 'Diskon', 'Grandtotal']
        for col in numeric_cols:
            if col in df.columns:
                # Menggunakan .fillna(0) untuk mengganti NaN dengan 0
                # Kemudian .astype(int) untuk mengkonversi ke integer
                df[col] = df[col].fillna(0).astype(int)

        return df
    except FileNotFoundError:
        st.info(f"File '{file_path}' tidak ditemukan. Akan membuat DataFrame kosong dengan kolom default.")
        return pd.DataFrame(columns=default_columns_for_empty_df)
    except Exception as e:
        st.error(f"Error saat memuat data dari {file_path}: {e}")
        return pd.DataFrame(columns=default_columns_for_empty_df)

def save_data(df, file_path):
    """Menyimpan DataFrame ke CSV."""
    try:
        df.to_csv(file_path, index=False)
        # Penting: Setelah menyimpan, hapus cache untuk data ini agar saat dimuat ulang
        # data terbaru yang sudah diperbarui tampil di Streamlit.
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Error saat menyimpan data ke {file_path}: {e}")

def show_spp_history():
    st.title("Riwayat Pembayaran SPP")

    # Muat data SPP
    df_spp = load_data(SPP_DATA_PATH)

    if df_spp.empty:
        st.info("Belum ada data pembayaran SPP tercatat.")
        return

    st.subheader("Tabel Riwayat SPP")
    
    # Hapus 'Nomor WhatsApp Orang Tua' dari kolom yang akan ditampilkan
    display_cols = ['Nomor Pembayaran', 'Tanggal', 'Nama Siswa', 'Bulan/Ujian', 'Jumlah', 'Diskon', 'Grandtotal']
    
    # Pastikan kolom yang akan ditampilkan benar-benar ada di DataFrame
    # Ini penting jika file CSV lama tidak memiliki semua kolom yang diharapkan
    actual_display_cols = [col for col in display_cols if col in df_spp.columns]

    st.dataframe(df_spp[actual_display_cols].sort_values(by='Tanggal', ascending=False), use_container_width=True)

    # --- Fungsi Edit & Hapus ---
    st.subheader("Edit atau Hapus Data SPP")
    
    # Buat pilihan untuk selectbox
    # Cek apakah kolom yang dibutuhkan ada sebelum membuat options
    if not df_spp.empty and \
       'Nomor Pembayaran' in df_spp.columns and \
       'Nama Siswa' in df_spp.columns and \
       'Bulan/Ujian' in df_spp.columns and \
       'Grandtotal' in df_spp.columns:
        
        # Pastikan kolom 'Grandtotal' sudah int sebelum format
        if df_spp['Grandtotal'].dtype != 'int64':
             df_spp['Grandtotal'] = df_spp['Grandtotal'].fillna(0).astype(int)

        options = df_spp.apply(lambda row: f"{row['Nomor Pembayaran']} - {row['Nama Siswa']} ({row['Bulan/Ujian']}) - Rp {row['Grandtotal']:,.0f}", axis=1).tolist()
    else:
        options = ["Tidak ada data yang dapat dipilih"]

    selected_option = st.selectbox("Pilih data untuk diedit atau dihapus", options, key="spp_select_edit_delete")
    
    # Dapatkan indeks dari data yang dipilih
    try:
        selected_index = options.index(selected_option) if selected_option != "Tidak ada data yang dapat dipilih" else None
    except ValueError: # Jika selected_option tidak ditemukan (misal setelah hapus)
        selected_index = None

    if selected_index is not None and not df_spp.empty:
        # Gunakan .copy() untuk menghindari SettingWithCopyWarning
        data_to_modify = df_spp.iloc[selected_index].copy()

        st.write(f"Anda memilih: **{selected_option}**")

        # Tombol Edit
        with st.expander("📝 Edit Data SPP"):
            st.write("Ubah data di bawah ini:")
            
            # Konversi tanggal string ke date object untuk st.date_input
            # Pastikan Tanggal adalah string YYYY-MM-DD
            current_date_str = str(data_to_modify.get('Tanggal', '')) # Ambil sebagai string
            
            current_date_val = None
            if current_date_str and current_date_str != '':
                try:
                    current_date_val = datetime.strptime(current_date_str, '%Y-%m-%d').date()
                except ValueError:
                    current_date_val = datetime.now().date() # Fallback jika format tidak sesuai
            else:
                current_date_val = datetime.now().date() # Default jika kosong

            edited_payment_id = st.text_input("Nomor Pembayaran", value=str(data_to_modify.get('Nomor Pembayaran', '')), disabled=True)
            edited_tanggal = st.date_input("Tanggal", value=current_date_val, key=f"edit_tanggal_{selected_index}")
            edited_kode_unik = st.text_input("Kode Unik Siswa", value=str(data_to_modify.get('Kode Unik Siswa', '')), key=f"edit_kode_unik_{selected_index}")
            edited_nama_siswa = st.text_input("Nama Siswa", value=str(data_to_modify.get('Nama Siswa', '')), key=f"edit_nama_siswa_{selected_index}")
            # Baris ini dihapus: edited_wa_ortu = st.text_input("Nomor WhatsApp Orang Tua", value=str(data_to_modify.get('Nomor WhatsApp Orang Tua', '')))
            edited_jenis_pembayaran = st.selectbox("Jenis Pembayaran", ['SPP', 'UTS', 'UAS'], index=['SPP', 'UTS', 'UAS'].index(data_to_modify.get('Jenis Pembayaran', 'SPP')), key=f"edit_jenis_pembayaran_{selected_index}")
            edited_bulan_ujian = st.text_input("Bulan/Ujian", value=str(data_to_modify.get('Bulan/Ujian', '')), key=f"edit_bulan_ujian_{selected_index}")
            
            edited_jumlah = st.number_input("Jumlah", value=int(data_to_modify.get('Jumlah', 0)), min_value=0, key=f"edit_jumlah_{selected_index}")
            edited_diskon = st.number_input("Diskon", value=int(data_to_modify.get('Diskon', 0)), min_value=0, key=f"edit_diskon_{selected_index}")

            edited_grandtotal = edited_jumlah - edited_diskon # Hitung ulang Grandtotal
            st.text_input("Grandtotal", value=f"{edited_grandtotal:,.0f}", disabled=True, key=f"edit_grandtotal_display_{selected_index}")

            if st.button("💾 Simpan Perubahan SPP", key=f"save_spp_edit_{selected_index}"):
                df_spp.loc[selected_index, 'Tanggal'] = edited_tanggal.strftime('%Y-%m-%d') # Simpan sebagai string YYYY-MM-DD
                df_spp.loc[selected_index, 'Kode Unik Siswa'] = edited_kode_unik
                df_spp.loc[selected_index, 'Nama Siswa'] = edited_nama_siswa
                # Baris ini dihapus: df_spp.loc[selected_index, 'Nomor WhatsApp Orang Tua'] = edited_wa_ortu
                df_spp.loc[selected_index, 'Jenis Pembayaran'] = edited_jenis_pembayaran
                df_spp.loc[selected_index, 'Bulan/Ujian'] = edited_bulan_ujian
                df_spp.loc[selected_index, 'Jumlah'] = edited_jumlah
                df_spp.loc[selected_index, 'Diskon'] = edited_diskon
                df_spp.loc[selected_index, 'Grandtotal'] = edited_grandtotal # Simpan grandtotal yang dihitung ulang

                save_data(df_spp, SPP_DATA_PATH)
                st.success("Data SPP berhasil diperbarui!")
                st.rerun()

        # Tombol Hapus
        if st.button("🗑️ Hapus Data SPP", key=f"delete_spp_btn_{selected_index}"):
            df_spp = df_spp.drop(df_spp.index[selected_index]).reset_index(drop=True)
            save_data(df_spp, SPP_DATA_PATH)
            st.success("Data SPP berhasil dihapus!")
            st.rerun()
    elif df_spp.empty:
        st.info("Tidak ada data untuk diedit atau dihapus.")
    else:
        st.info("Silakan pilih data dari daftar di atas untuk mengedit atau menghapus.")

# --- Panggil Fungsi Utama ---
if __name__ == '__main__':
    show_spp_history()