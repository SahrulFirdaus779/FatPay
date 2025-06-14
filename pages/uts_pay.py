import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Asumsi lokasi file ini adalah di folder 'pages'
UTS_DATA_PATH = 'uts_data.csv'

@st.cache_data
def load_data(file_path):
    """
    Memuat data dari CSV, mengembalikan DataFrame kosong jika file tidak ditemukan.
    Mengisi NaN di kolom numerik dengan 0 dan mengkonversinya ke int.
    Memastikan kolom Tanggal diformat dengan benar dan mengganti NaT dengan string kosong.
    """
    # Kolom default harus sesuai dengan apa yang disimpan oleh payment_form.py
    default_columns_for_empty_df = [
        'Nomor Pembayaran', 'Tanggal', 'Kode Unik Siswa', 'Nama Siswa',
        'Jenis Pembayaran', 'Bulan/Ujian', 'Jumlah', 'Diskon', 'Grandtotal'
    ]
    try:
        if not os.path.exists(file_path):
            return pd.DataFrame(columns=default_columns_for_empty_df)

        df = pd.read_csv(file_path)

        if 'Tanggal' in df.columns:
            df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
            df['Tanggal'] = df['Tanggal'].dt.strftime('%Y-%m-%d').fillna('')
            
        numeric_cols = ['Jumlah', 'Diskon', 'Grandtotal']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0).astype(int)

        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=default_columns_for_empty_df)
    except Exception as e:
        st.error(f"Error saat memuat data dari {file_path}: {e}")
        return pd.DataFrame(columns=default_columns_for_empty_df)

def save_data(df, file_path):
    """Menyimpan DataFrame ke CSV."""
    try:
        df.to_csv(file_path, index=False)
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Error saat menyimpan data ke {file_path}: {e}")

def show_uts_history():
    st.title("Riwayat Pembayaran UTS")

    df_uts = load_data(UTS_DATA_PATH)

    if df_uts.empty:
        st.info("Belum ada data pembayaran UTS tercatat.")
        return

    st.subheader("Tabel Riwayat UTS")
    
    display_cols = ['Nomor Pembayaran', 'Tanggal', 'Nama Siswa', 'Bulan/Ujian', 'Jumlah', 'Diskon', 'Grandtotal']
    actual_display_cols = [col for col in display_cols if col in df_uts.columns]
    
    if 'Tanggal' in actual_display_cols:
        df_uts_display = df_uts[actual_display_cols].copy()
        df_uts_display['Tanggal_Sort'] = pd.to_datetime(df_uts_display['Tanggal'], errors='coerce')
        st.dataframe(df_uts_display.sort_values(by='Tanggal_Sort', ascending=False).drop(columns=['Tanggal_Sort']), use_container_width=True)
    else:
        st.dataframe(df_uts[actual_display_cols], use_container_width=True)


    st.subheader("Edit atau Hapus Data UTS")
    
    if not df_uts.empty and \
       'Nomor Pembayaran' in df_uts.columns and \
       'Nama Siswa' in df_uts.columns and \
       'Bulan/Ujian' in df_uts.columns and \
       'Grandtotal' in df_uts.columns:
        
        if df_uts['Grandtotal'].dtype != 'int64':
             df_uts['Grandtotal'] = df_uts['Grandtotal'].fillna(0).astype(int)

        options = df_uts.apply(lambda row: f"{row['Nomor Pembayaran']} - {row['Nama Siswa']} ({row['Bulan/Ujian']}) - Rp {row['Grandtotal']:,.0f}", axis=1).tolist()
    else:
        options = ["Tidak ada data yang dapat dipilih"]

    selected_option = st.selectbox("Pilih data untuk diedit atau dihapus", options, key="uts_select_edit_delete")
    
    try:
        selected_index = options.index(selected_option) if selected_option != "Tidak ada data yang dapat dipilih" else None
    except ValueError:
        selected_index = None

    if selected_index is not None and not df_uts.empty:
        data_to_modify = df_uts.iloc[selected_index].copy()

        st.write(f"Anda memilih: **{selected_option}**")

        with st.expander("📝 Edit Data UTS"):
            st.write("Ubah data di bawah ini:")
            
            current_date_str = str(data_to_modify.get('Tanggal', ''))
            
            current_date_val = None
            if current_date_str and current_date_str != '':
                try:
                    current_date_val = datetime.strptime(current_date_str, '%Y-%m-%d').date()
                except ValueError:
                    current_date_val = datetime.now().date()
            else:
                current_date_val = datetime.now().date()

            edited_payment_id = st.text_input("Nomor Pembayaran", value=str(data_to_modify.get('Nomor Pembayaran', '')), disabled=True)
            edited_tanggal = st.date_input("Tanggal", value=current_date_val, key=f"uts_edit_tanggal_{selected_index}")
            edited_kode_unik = st.text_input("Kode Unik Siswa", value=str(data_to_modify.get('Kode Unik Siswa', '')), key=f"uts_edit_kode_unik_{selected_index}")
            edited_nama_siswa = st.text_input("Nama Siswa", value=str(data_to_modify.get('Nama Siswa', '')), key=f"uts_edit_nama_siswa_{selected_index}")
            edited_jenis_pembayaran = st.selectbox("Jenis Pembayaran", ['SPP', 'UTS', 'UAS'], index=['SPP', 'UTS', 'UAS'].index(data_to_modify.get('Jenis Pembayaran', 'UTS')), key=f"uts_edit_jenis_pembayaran_{selected_index}")
            edited_bulan_ujian = st.text_input("Bulan/Ujian", value=str(data_to_modify.get('Bulan/Ujian', '')), key=f"uts_edit_bulan_ujian_{selected_index}")
            
            edited_jumlah = st.number_input("Jumlah", value=int(data_to_modify.get('Jumlah', 0)), min_value=0, key=f"uts_edit_jumlah_{selected_index}")
            edited_diskon = st.number_input("Diskon", value=int(data_to_modify.get('Diskon', 0)), min_value=0, key=f"uts_edit_diskon_{selected_index}")

            edited_grandtotal = edited_jumlah - edited_diskon
            st.text_input("Grandtotal", value=f"{edited_grandtotal:,.0f}", disabled=True, key=f"uts_edit_grandtotal_display_{selected_index}")

            if st.button("💾 Simpan Perubahan UTS", key=f"save_uts_edit_{selected_index}"):
                df_uts.loc[selected_index, 'Tanggal'] = edited_tanggal.strftime('%Y-%m-%d')
                df_uts.loc[selected_index, 'Kode Unik Siswa'] = edited_kode_unik
                df_uts.loc[selected_index, 'Nama Siswa'] = edited_nama_siswa
                df_uts.loc[selected_index, 'Jenis Pembayaran'] = edited_jenis_pembayaran
                df_uts.loc[selected_index, 'Bulan/Ujian'] = edited_bulan_ujian
                df_uts.loc[selected_index, 'Jumlah'] = edited_jumlah
                df_uts.loc[selected_index, 'Diskon'] = edited_diskon
                df_uts.loc[selected_index, 'Grandtotal'] = edited_grandtotal

                save_data(df_uts, UTS_DATA_PATH)
                st.success("Data UTS berhasil diperbarui!")
                st.rerun()

        if st.button("🗑️ Hapus Data UTS", key=f"delete_uts_btn_{selected_index}"):
            df_uts = df_uts.drop(df_uts.index[selected_index]).reset_index(drop=True)
            save_data(df_uts, UTS_DATA_PATH)
            st.success("Data UTS berhasil dihapus!")
            st.rerun()
    elif df_uts.empty:
        st.info("Tidak ada data untuk diedit atau dihapus.")
    else:
        st.info("Silakan pilih data dari daftar di atas untuk mengedit atau menghapus.")

if __name__ == '__main__':
    show_uts_history()
