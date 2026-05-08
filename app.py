import streamlit as st
import yfinance as yf
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pypdf import PdfReader
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests

# --- 1. PENGATURAN HALAMAN ---
st.set_page_config(page_title="FintechAI - Dashboard", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# --- 2. FUNGSI UNTUK ANIMASI LOTTIE ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Load animasi "AI Thinking"
lottie_thinking = load_lottieurl("https://lottie.host/786bd49b-7cc2-4df7-873d-9d41315fc472/rJ4w2A61qK.json") 

# --- 3. KONEKSI KE SERVER AMD ---
@st.cache_resource
def init_llm():
    return ChatOpenAI(
        base_url="http://165.245.143.132:8000/v1", # PASTIKAN IP INI BENAR
        api_key="kosong", 
        model="Qwen/Qwen2.5-1.5B-Instruct",
        max_tokens=1200
    )
llm = init_llm()

# --- 4. INJEKSI CSS (HERO BANNER & CARD AI) ---
custom_css = """
<style>
    .hero-banner {
        background: linear-gradient(135deg, #0E1117 0%, #1a2333 100%);
        padding: 30px 20px; border-radius: 12px; text-align: center;
        border: 1px solid #333; margin-bottom: 30px; box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
    }
    .app-title { font-size: 3.2rem; font-weight: 800; background: -webkit-linear-gradient(45deg, #00E676, #00b0ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px;}
    .app-subtitle { color: #a0aec0; font-size: 1.1rem; margin-bottom: 15px;}
    .terminal-window { background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; width: 80%; max-width: 650px; margin: 0 auto; text-align: left; font-family: monospace; overflow: hidden;}
    .terminal-header { background-color: #161b22; padding: 10px; display: flex; gap: 8px; border-bottom: 1px solid #30363d;}
    .t-dot { height: 12px; width: 12px; border-radius: 50%; }
    .red { background-color: #ff5f56; } .yellow { background-color: #ffbd2e; } .green { background-color: #27c93f; }
    .terminal-body { padding: 15px; color: #c9d1d9; line-height: 1.5; font-size: 14px;}
    .cmd-user { color: #00E676; font-weight: bold; }
    .cursor { display: inline-block; width: 8px; height: 15px; background-color: #00E676; animation: blink 1s step-end infinite; }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
    .ai-card {
        background-color: #1E2127; padding: 25px; border-radius: 12px;
        border-left: 5px solid #00E676; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-top: 20px; color: #E2E8F0; font-size: 1rem; line-height: 1.6;
    }
</style>
"""

hero_html = """
<div class="hero-banner">
    <h1 class="app-title">FintechAI</h1>
    <p class="app-subtitle">Sistem Analitik Finansial Otonom dengan Komputasi Edge GPU</p>
    <div class="terminal-window">
        <div class="terminal-header"><div class="t-dot red"></div><div class="t-dot yellow"></div><div class="t-dot green"></div></div>
        <div class="terminal-body"><span class="cmd-user">root@amd-server:~#</span> ./start_fintech_engine.sh<br><span class="cmd-text">[INFO] Initializing Qwen-1.5B on MI300X... OK</span><br><span class="cmd-user">root@amd-server:~#</span> Awaiting command<span class="cursor"></span></div>
    </div>
</div>
"""
st.markdown(custom_css + hero_html, unsafe_allow_html=True)

# --- 5. SIDEBAR MENU ---
with st.sidebar:
    # 1. Menampilkan gambar landscape bbtech.jpg Anda
    try:
        # Parameter use_container_width akan membuat gambar otomatis menyesuaikan lebar sidebar
        st.image("bbtech.jpg", use_container_width=True)
    except:
        # Jika gambar belum ada di folder, beri pesan sementara
        st.caption("*(Gambar bbtech.jpg belum ditaruh di folder proyek)*")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Trik menyulap Logo AMD Hitam menjadi Putih menggunakan CSS Filter
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/7/7c/AMD_Logo.svg" 
                 style="width: 120px; filter: brightness(0) invert(1);">
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # 3. Menu Navigasi dengan warna baru
    pilihan_menu = option_menu(
        menu_title=None, # Dihilangkan agar lebih clean karena sudah ada gambar bbtech
        options=["Analisis Saham", "Bedah PDF Laporan"],
        icons=["graph-up-arrow", "file-earmark-pdf"],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#00FFA3", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px 0px", "border-radius":"8px", "--hover-color": "#334155"},
            "nav-link-selected": {"background-color": "#1E293B", "color": "#00FFA3", "font-weight": "bold", "border-left": "4px solid #00FFA3"},
        }
    )

# --- 6. LOGIKA HALAMAN UTAMA ---

if pilihan_menu == "Analisis Saham":
    st.header("📊 Analisis Sentimen & Teknikal")
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        ticker_input = st.text_input("Kode Saham (contoh: BBCA.JK, AAPL):", "BBCA.JK")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True) # Spacer
        tombol_analisis = st.button("Jalankan Analisis", type="primary", use_container_width=True)
        
    if tombol_analisis:
        anim_placeholder = st.empty()
        with anim_placeholder.container():
            if lottie_thinking: st_lottie(lottie_thinking, height=150, key="loading_saham")
            st.markdown("<h5 style='text-align:center; color:#00E676;'>Menarik data pasar dan sentimen berita...</h5>", unsafe_allow_html=True)
            
        try:
            saham = yf.Ticker(ticker_input)
            hist = saham.history(period="1mo")
            
            if hist.empty:
                anim_placeholder.empty()
                st.error("Data saham tidak ditemukan. Pastikan kode benar.")
            else:
                # Perhitungan Metrik
                harga_terakhir = hist['Close'].iloc[-1]
                harga_awal_bulan = hist['Close'].iloc[0]
                harga_tertinggi = hist['High'].max()
                harga_terendah = hist['Low'].min()
                perubahan = harga_terakhir - harga_awal_bulan
                persentase = (perubahan / harga_awal_bulan) * 100
                tren = "Bullish (Naik)" if harga_terakhir > harga_awal_bulan else "Bearish (Turun)"
                
                # Tarik Berita
                berita = saham.news[:3] if hasattr(saham, 'news') else []
                teks_berita = "\n".join([f"- {b['title']}" for b in berita]) if berita else "Tidak ada berita terbaru."
                
                anim_placeholder.empty() # Hapus animasi
                
                # UI Dashboard Eksekutif
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Harga Saat Ini", f"{harga_terakhir:.2f}", f"{perubahan:.2f} ({persentase:.2f}%)")
                col_m2.metric("Resistance (Tertinggi)", f"{harga_tertinggi:.2f}")
                col_m3.metric("Support (Terendah)", f"{harga_terendah:.2f}")
                
                # Progress Bar
                st.caption("📍 Posisi Harga Saat Ini (Support ↔ Resistance)")
                rentang_harga = harga_tertinggi - harga_terendah
                posisi_persen = (harga_terakhir - harga_terendah) / rentang_harga if rentang_harga > 0 else 0.5
                st.progress(float(max(0, min(1, posisi_persen))))
                
                # Berita & Chart
                with st.expander("📰 Sentimen Pasar Saat Ini (Berita Terbaru)", expanded=True):
                    st.write(teks_berita)
                st.line_chart(hist['Close'])
                
                # Pemanggilan AI
                data_ringkas = f"Kode: {ticker_input}\nHarga: {harga_terakhir:.2f}\nSupport: {harga_terendah:.2f}\nResistance: {harga_tertinggi:.2f}\nTren: {tren}\nBerita:\n{teks_berita}"
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", "Kamu analis saham profesional. Berikan analisis tren, dampak berita, dan saran ENTRY yang aman (jika bullish). Gunakan bahasa Indonesia."),
                    ("user", "Data Pasar:\n{data}")
                ])
                jawaban = (prompt_template | llm).invoke({"data": data_ringkas})
                
                # Output Card
                st.markdown(f'<div class="ai-card"><h4>🤖 Analisis FintechAI</h4>{jawaban.content}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button("📥 Unduh Laporan Saham (.txt)", jawaban.content, f"Laporan_{ticker_input}.txt", mime="text/plain")
                
        except Exception as e:
            anim_placeholder.empty()
            st.error(f"Terjadi kesalahan: {e}")

elif pilihan_menu == "Bedah PDF Laporan":
    st.header("📄 Pemindai Laporan Finansial")
    st.markdown("Algoritma **Keyword Hunter** akan menyeleksi halaman paling relevan dari Annual Report.")
    
    uploaded_file = st.file_uploader("Upload dokumen keuangan (PDF)", type="pdf")
    pertanyaan_user = st.text_input("Apa yang ingin kamu ketahui dari laporan ini?", "Tolong buatkan ringkasan laba dan pendapatan dari dokumen ini.")
    
    if uploaded_file and st.button("Mulai Bedah Dokumen", type="primary"):
        anim_placeholder = st.empty()
        with anim_placeholder.container():
            if lottie_thinking: st_lottie(lottie_thinking, height=150, key="loading_pdf")
            st.markdown("<h5 style='text-align:center; color:#00E676;'>Mengekstrak dan membaca dokumen...</h5>", unsafe_allow_html=True)
            
        try:
            pdf_reader = PdfReader(uploaded_file)
            teks_dokumen = ""
            kata_kunci = ["laba", "pendapatan", "risiko", "prospek", "aset", "liabilitas", "rugi"]
            halaman_ditemukan = 0
            
            for i, page in enumerate(pdf_reader.pages):
                teks_halaman = page.extract_text()
                if teks_halaman and any(k in teks_halaman.lower() for k in kata_kunci):
                    teks_dokumen += f"--- HALAMAN {i+1} ---\n{teks_halaman}\n\n"
                    halaman_ditemukan += 1
                if halaman_ditemukan >= 15: break
            
            # Logika Rencana B (Fallback)
            if halaman_ditemukan == 0:
                anim_placeholder.empty()
                st.warning("⚠️ Dokumen tidak menggunakan format keuangan standar. Beralih ke Mode Ekstraksi Umum...")
                
                total_pages = len(pdf_reader.pages)
                sampel_awal = list(range(min(3, total_pages)))
                sampel_tengah = list(range(max(3, total_pages//2), min(total_pages, (total_pages//2) + 3)))
                
                for i in sorted(list(set(sampel_awal + sampel_tengah))):
                    teks_dokumen += f"--- HALAMAN {i+1} ---\n{pdf_reader.pages[i].extract_text()}\n\n"
                
                prompt_aktif = ChatPromptTemplate.from_messages([
                    ("system", """Kamu Analis Dokumen Profesional. Buat ringkasan untuk menjawab pertanyaan.
                    ATURAN KRITIS: Jika teks sama sekali tidak membahas perusahaan/keuangan/ekonomi, TOLAK dengan menjawab: "Dokumen yang diberikan tidak sesuai. Mohon unggah dokumen terkait finansial." """),
                    ("user", "Dokumen:\n{dokumen}\n\nPertanyaan: {pertanyaan}")
                ])
            else:
                anim_placeholder.empty()
                st.success(f"Berhasil mengekstrak {halaman_ditemukan} halaman krusial.")
                prompt_aktif = ChatPromptTemplate.from_messages([
                    ("system", "Kamu Auditor Keuangan Senior. Jawab pertanyaan pengguna dengan akurat berdasarkan teks lampiran. Gunakan bullet points."),
                    ("user", "Dokumen:\n{dokumen}\n\nPertanyaan: {pertanyaan}")
                ])
                
            # Pemanggilan AI
            jawaban_pdf = (prompt_aktif | llm).invoke({"dokumen": teks_dokumen, "pertanyaan": pertanyaan_user})
            
            # Output Card
            st.markdown(f'<div class="ai-card"><h4>🤖 Jawaban Auditor FintechAI</h4>{jawaban_pdf.content}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("📥 Unduh Hasil Bedah PDF (.txt)", jawaban_pdf.content, "Hasil_Bedah_PDF.txt", mime="text/plain")

        except Exception as e:
            anim_placeholder.empty()
            st.error(f"Terjadi kesalahan saat membaca PDF: {e}")
            