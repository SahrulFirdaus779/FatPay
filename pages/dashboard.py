import streamlit as st
import pandas as pd

# Path ke file CSV Anda
SPP_DATA_PATH = 'spp_data.csv'
UTS_DATA_PATH = 'uts_data.csv'
UAS_DATA_PATH = 'uas_data.csv'

def load_data(file_path):
    """Memuat data dari CSV, mengembalikan DataFrame kosong jika file tidak ditemukan."""
    try:
        df = pd.read_csv(file_path)
        # Pastikan kolom Tanggal adalah datetime
        if 'Tanggal' in df.columns:
            df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
        return df
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error saat memuat data dari {file_path}: {e}")
        return pd.DataFrame()

def show_dashboard():
    st.title("Dashboard FatPay")

    spp_df = load_data(SPP_DATA_PATH)
    uts_df = load_data(UTS_DATA_PATH)
    uas_df = load_data(UAS_DATA_PATH)

    st.header("Ringkasan Pembayaran Keseluruhan")

    total_spp = spp_df['Grandtotal'].sum() if 'Grandtotal' in spp_df.columns and not spp_df.empty else 0
    total_uts = uts_df['Grandtotal'].sum() if 'Grandtotal' in uts_df.columns and not uts_df.empty else 0
    total_uas = uas_df['Grandtotal'].sum() if 'Grandtotal' in uas_df.columns and not uas_df.empty else 0
    
    total_keseluruhan = total_spp + total_uts + total_uas

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Total Pembayaran SPP", value=f"Rp {total_spp:,.0f}")
    with col2:
        st.metric(label="Total Pembayaran UTS", value=f"Rp {total_uts:,.0f}")
    with col3:
        st.metric(label="Total Pembayaran UAS", value=f"Rp {total_uas:,.0f}")
    with col4:
        st.metric(label="Total Pembayaran Keseluruhan", value=f"Rp {total_keseluruhan:,.0f}")

    st.markdown("---")

    st.header("Data Pembayaran Terbaru")
    
    # Menggabungkan semua dataframe untuk tampilan terbaru
    all_payments = pd.DataFrame()
    if not spp_df.empty:
        all_payments = pd.concat([all_payments, spp_df.assign(Jenis='SPP')], ignore_index=True)
    if not uts_df.empty:
        all_payments = pd.concat([all_payments, uts_df.assign(Jenis='UTS')], ignore_index=True)
    if not uas_df.empty:
        all_payments = pd.concat([all_payments, uas_df.assign(Jenis='UAS')], ignore_index=True)

    if not all_payments.empty:
        # Sort by Tanggal in descending order and show latest 10
        all_payments = all_payments.sort_values(by='Tanggal', ascending=False)
        st.subheader("Semua Pembayaran Terbaru")
        # Pilih kolom yang relevan untuk ditampilkan
        display_cols = ['Tanggal', 'Nomor Pembayaran', 'Nama Siswa', 'Jenis Pembayaran', 'Bulan/Ujian', 'Jumlah', 'Diskon', 'Grandtotal']
        # Filter kolom yang benar-benar ada di dataframe
        display_cols = [col for col in display_cols if col in all_payments.columns]
        st.dataframe(all_payments[display_cols].head(10), use_container_width=True)
    else:
        st.info("Belum ada data pembayaran tercatat.")