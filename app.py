import streamlit as st
import pandas as pd
import io

# 1. Menaikkan limit elemen styler pandas untuk menangani jutaan sel data
pd.set_option("styler.render.max_elements", 5000000)

st.set_page_config(page_title="SITI - Pembanding Data", layout="wide", page_icon="🔍")

# Header Aplikasi
st.markdown("<h1 style='text-align: center; color: #4F81BD;'>🔍 SITI: Data Matcher</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; font-weight: normal;'>Modul Pelacak Kesamaan & Perbedaan Berkas</h4>", unsafe_allow_html=True)
st.divider()

st.write("Aplikasi ini membantu Anda mengidentifikasi dengan cepat data mana saja yang **SAMA (Cocok)** dan data mana saja yang **TIDAK SAMA (Tidak Ada Pasangannya)** di antara kedua berkas.")

# Pengaturan Tata Letak Kolom Unggah Berkas
col1, col2 = st.columns(2)

with col1:
    st.subheader("📁 Berkas Pertama (File A)")
    file_a = st.file_uploader("Unggah File A (.xlsx, .xls, .csv)", type=["xlsx", "xls", "csv"], key="file_a")

with col2:
    st.subheader("📁 Berkas Kedua (File B)")
    file_b = st.file_uploader("Unggah File B (.xlsx, .xls, .csv)", type=["xlsx", "xls", "csv"], key="file_b")

if file_a and file_b:
    # Membaca data File A
    try:
        df_a = pd.read_csv(file_a, on_bad_lines='skip') if file_a.name.endswith('.csv') else pd.read_excel(file_a)
    except Exception as e:
        st.error(f"Gagal membaca File A: {e}")
        df_a = None

    # Membaca data File B
    try:
        df_b = pd.read_csv(file_b, on_bad_lines='skip') if file_b.name.endswith('.csv') else pd.read_excel(file_b)
    except Exception as e:
        st.error(f"Gagal membaca File B: {e}")
        df_b = None

    if df_a is not None and df_b is not None:
        st.success(f"File berhasil dimuat! File A ({len(df_a)} baris) | File B ({len(df_b)} baris)")
        st.divider()
        
        st.subheader("⚙️ Pengaturan Kolom Kunci & Analisis")
        
        col_select_1, col_select_2, col_select_3 = st.columns(3)
        with col_select_1:
            key_a = st.selectbox("Kolom Kunci File A", options=df_a.columns)
        with col_select_2:
            key_b = st.selectbox("Kolom Kunci File B", options=df_b.columns)
        with col_select_3:
            # Menu filter yang mengakomodasi kebutuhan Anda untuk melihat data tidak sama
            filter_view = st.selectbox("Tampilan Data di Layar", [
                "Hanya Tampilkan Data yang TIDAK SAMA (Tidak Ada Pasangannya)",
                "Hanya Tampilkan Data yang SAMA (Cocok)",
                "Tampilkan Semua Data (Beri Warna Kuning pada Data yang Sama)"
            ])
            
        if st.button("Mulai Analisis Perbandingan", type="primary"):
            with st.spinner("Sedang menganalisis jutaan sel data..."):
                # Salin data untuk dibersihkan spasinya agar akurat
                df_a_clean = df_a.copy()
                df_b_clean = df_b.copy()
                
                df_a_clean['__match_key__'] = df_a_clean[key_a].astype(str).str.strip().str.lower()
                df_b_clean['__match_key__'] = df_b_clean[key_b].astype(str).str.strip().str.lower()
                
                # Menggunakan Set untuk pencarian cepat data berukuran besar
                keys_in_b = set(df_b_clean['__match_key__'].unique())
                keys_in_a = set(df_a_clean['__match_key__'].unique())
                
                # Logika Pemisahan Data Sama vs Tidak Sama
                # File A
                df_a_sama = df_a_clean[df_a_clean['__match_key__'].isin(keys_in_b)]
                df_a_beda = df_a_clean[~df_a_clean['__match_key__'].isin(keys_in_b)]
                
                # File B
                df_b_sama = df_b_clean[df_b_clean['__match_key__'].isin(keys_in_a)]
                df_b_beda = df_b_clean[~df_b_clean['__match_key__'].isin(keys_in_a)]
                
                # -----------------------------
                # PANEL STATISTIK / METRIK
                # -----------------------------
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric(label="Data SAMA (Ada di A & B)", value=f"{len(df_a_sama)} baris")
                with m_col2:
                    st.metric(label="Data di File A (TIDAK ADA di B)", value=f"{len(df_a_beda)} baris")
                with m_col3:
                    st.metric(label="Data di File B (TIDAK ADA di A)", value=f"{len(df_b_beda)} baris")
                
                st.divider()

                # Menentukan data mana yang akan dirender ke layar sesuai filter terpilih
                if filter_view == "Hanya Tampilkan Data yang TIDAK SAMA (Tidak Ada Pasangannya)":
                    df_a_disp = df_a_beda.copy()
                    df_b_disp = df_b_beda.copy()
                    mode_style = "diff"
                elif filter_view == "Hanya Tampilkan Data yang SAMA (Cocok)":
                    df_a_disp = df_a_sama.copy()
                    df_b_disp = df_b_sama.copy()
                    mode_style = "same"
                else:
                    df_a_disp = df_a_clean.copy()
                    df_b_disp = df_b_clean.copy()
                    mode_style = "all"
                
                # Fungsi pewarnaan visual (hanya aktif jika menampilkan semua data)
                def highlight_matches_a(row):
                    return ['background-color: #FFF2CC' if row['__match_key__'] in keys_in_b else '' for _ in row]
                    
                def highlight_matches_b(row):
                    return ['background-color: #FFF2CC' if row['__match_key__'] in keys_in_a else '' for _ in row]
                
                # -----------------------------
                # TAMPILAN PRATINJAU TABEL DI WEB
                # -----------------------------
                tab_res1, tab_res2 = st.tabs([
                    f"📄 Preview File A ({len(df_a_disp)} baris ditampilkan)", 
                    f"📄 Preview File B ({len(df_b_disp)} baris ditampilkan)"
                ])
                
                with tab_res1:
                    if not df_a_disp.empty:
                        df_display_a = df_a_disp.drop(columns=['__match_key__'])
                        if mode_style == "all":
                            st.dataframe(df_display_a.style.apply(highlight_matches_a, axis=1), use_container_width=True)
                        else:
                            st.dataframe(df_display_a, use_container_width=True)
                    else:
                        st.info("Tidak ada data yang sesuai filter untuk ditampilkan.")
                        
                with tab_res2:
                    if not df_b_disp.empty:
                        df_display_b = df_b_disp.drop(columns=['__match_key__'])
                        if mode_style == "all":
                            st.dataframe(df_display_b.style.apply(highlight_matches_b, axis=1), use_container_width=True)
                        else:
                            st.dataframe(df_display_b, use_container_width=True)
                    else:
                        st.info("Tidak ada data yang sesuai filter untuk ditampilkan.")
                
                st.divider()
                
                # -----------------------------
                # TOMBOL UNDUH EXCEL TERPISAH
                # -----------------------------
                st.subheader("📥 Unduh Hasil Ekspor Analisis")
                st.write("Anda bisa mengunduh berkas Excel yang sudah langsung dipisahkan berdasarkan kategori kelayakannya:")
                
                down_col1, down_col2 = st.columns(2)
                
                with down_col1:
                    # Excel 1: Berisi khusus data yang TIDAK SAMA (Hilang/Kotor)
                    output_beda = io.BytesIO()
                    with pd.ExcelWriter(output_beda, engine='openpyxl') as writer:
                        df_a_beda.drop(columns=['__match_key__']).to_excel(writer, sheet_name='Hanya di File A', index=False)
                        df_b_beda.drop(columns=['__match_key__']).to_excel(writer, sheet_name='Hanya di File B', index=False)
                    
                    st.download_button(
                        label="❌ Unduh Data yang TIDAK SAMA (.xlsx)",
                        data=output_beda.getvalue(),
                        file_name="SITI_Data_TIDAK_SAMA.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                with down_col2:
                    # Excel 2: Berisi khusus data yang SAMA (Duplikat/Cocok)
                    output_sama = io.BytesIO()
                    with pd.ExcelWriter(output_sama, engine='openpyxl') as writer:
                        df_a_sama.drop(columns=['__match_key__']).to_excel(writer, sheet_name='Cocok di File A', index=False)
                        df_b_sama.drop(columns=['__match_key__']).to_excel(writer, sheet_name='Cocok di File B', index=False)
                        
                    st.download_button(
                        label="✅ Unduh Data yang SAMA / COCOK (.xlsx)",
                        data=output_sama.getvalue(),
                        file_name="SITI_Data_SAMA_COCOK.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
