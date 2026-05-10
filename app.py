import streamlit as st
import yfinance as yf
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pypdf import PdfReader
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests

# --- 1. PENGATURAN HALAMAN---
st.set_page_config(page_title="FintechAI - Dashboard", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# --- 2. FUNGSI UNTUK ANIMASI & MARKET DATA ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_thinking = load_lottieurl("https://lottie.host/786bd49b-7cc2-4df7-873d-9d41315fc472/rJ4w2A61qK.json") 

@st.cache_data(ttl=300)
def get_global_market_pulse():
    tickers = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "BTC/USD": "BTC-USD", "Gold": "GC=F"}
    data = {}
    for name, symbol in tickers.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                harga_sekarang = hist['Close'].iloc[-1]
                harga_kemarin = hist['Close'].iloc[-2]
                persentase = ((harga_sekarang - harga_kemarin) / harga_kemarin) * 100
                data[name] = {"val": harga_sekarang, "pct": persentase}
            else: data[name] = None
        except: data[name] = None
    return data

# --- 3. KONEKSI KE SERVER AMD ---
@st.cache_resource
def init_llm():
    return ChatOpenAI(
        base_url="http://134.199.195.117:8000/v1", # PASTIKAN IP SERVER AMD KAMU BENAR
        api_key="kosong", 
        model="Qwen/Qwen2.5-1.5B-Instruct",
        max_tokens=1200
    )
llm = init_llm()

# --- 4. INJEKSI CSS PURE (UI MODERN) ---
custom_css = """
<style>
    .hero-banner {
        background: linear-gradient(135deg, #0E1117 0%, #1a2333 100%);
        padding: 30px 20px; border-radius: 12px; text-align: center;
        border: 1px solid #333; margin-bottom: 30px; box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
    }
    .app-title { font-size: 3.2rem; font-weight: 800; background: -webkit-linear-gradient(45deg, #00FFA3, #00b0ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px;}
    .app-subtitle { color: #a0aec0; font-size: 1.1rem; margin-bottom: 15px;}
    .terminal-window { background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; width: 80%; max-width: 650px; margin: 0 auto; text-align: left; font-family: monospace; overflow: hidden;}
    .terminal-header { background-color: #161b22; padding: 10px; display: flex; gap: 8px; border-bottom: 1px solid #30363d;}
    .t-dot { height: 12px; width: 12px; border-radius: 50%; }
    .red { background-color: #ff5f56; } .yellow { background-color: #ffbd2e; } .green { background-color: #27c93f; }
    .terminal-body { padding: 15px; color: #c9d1d9; line-height: 1.5; font-size: 14px;}
    .cmd-user { color: #00FFA3; font-weight: bold; }
    .cursor { display: inline-block; width: 8px; height: 15px; background-color: #00FFA3; animation: blink 1s step-end infinite; }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
    .ai-card { background-color: #1E293B; padding: 25px; border-radius: 12px; border-left: 5px solid #00FFA3; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-top: 20px; color: #E2E8F0; font-size: 1rem; line-height: 1.6;}
</style>
"""

hero_html = """
<div class="hero-banner">
    <h1 class="app-title">FintechAI</h1>
    <p class="app-subtitle">Autonomous Financial Analytics System (Edge GPU Computing)</p>
    <div class="terminal-window">
        <div class="terminal-header"><div class="t-dot red"></div><div class="t-dot yellow"></div><div class="t-dot green"></div></div>
        <div class="terminal-body"><span class="cmd-user">root@amd-server:~#</span> ./start_fintech_engine.sh<br><span style="color:#8b949e">[INFO] Initializing Qwen-1.5B on AMD MI300X... OK</span><br><span class="cmd-user">root@amd-server:~#</span> Awaiting command<span class="cursor"></span></div>
    </div>
</div>
"""
st.markdown(custom_css + hero_html, unsafe_allow_html=True)

# --- 5. SIDEBAR MENU ---
with st.sidebar:
    try:
        st.image("bbtech.jpg", use_container_width=True)
    except: pass
    
    st.markdown("""<div style="text-align: center; margin-bottom: 20px;"><img src="https://upload.wikimedia.org/wikipedia/commons/7/7c/AMD_Logo.svg" style="width: 120px; filter: brightness(0) invert(1);"></div>""", unsafe_allow_html=True)
    
    menu_choice = option_menu(
        menu_title=None,
        options=["Stock Analysis", "PDF Report Analyzer", "Portfolio Advisor"],
        icons=["graph-up-arrow", "file-earmark-pdf", "briefcase"],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#00FFA3", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px 0px", "border-radius":"8px", "--hover-color": "#334155"},
            "nav-link-selected": {"background-color": "#1E293B", "color": "#00FFA3", "font-weight": "bold", "border-left": "4px solid #00FFA3"},
        }
    )

# ==========================================
# GLOBAL MARKET PULSE (TAMPIL DI SEMUA MENU)
# ==========================================
st.markdown("##### 🌐 Global Market Pulse")
market_data = get_global_market_pulse()
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

def render_metric(col, name, prefix=""):
    info = market_data.get(name)
    if info is not None:
        col.metric(label=name, value=f"{prefix}{info['val']:,.2f}", delta=f"{info['pct']:.2f}%")
    else:
        col.metric(label=name, value="N/A", delta="N/A", delta_color="off")

render_metric(m_col1, "S&P 500")
render_metric(m_col2, "NASDAQ")
render_metric(m_col3, "BTC/USD", prefix="$")
render_metric(m_col4, "Gold", prefix="$")
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. MAIN PAGE LOGIC (BERDASARKAN MENU)
# ==========================================

if menu_choice == "Stock Analysis":
    st.header("📊 Sentiment & Technical Analysis")
    st.caption("🔥 **Trending today:** AAPL, NVDA, TSLA, MSFT, BBCA.JK")
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        ticker_input = st.text_input("Stock Ticker (e.g., BBCA.JK, AAPL):", "BBCA.JK")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("Run Analysis", type="primary", use_container_width=True)
        
    if analyze_button:
        anim_placeholder = st.empty()
        with anim_placeholder.container():
            if lottie_thinking: st_lottie(lottie_thinking, height=150, key="loading_stock")
            st.markdown("<h5 style='text-align:center; color:#00FFA3;'>Pulling market data and news sentiment...</h5>", unsafe_allow_html=True)
            
        try:
            stock = yf.Ticker(ticker_input)
            hist = stock.history(period="1mo")
            
            if hist.empty:
                anim_placeholder.empty()
                st.error("Stock data not found. Ensure the ticker is correct.")
            else:
                last_price = hist['Close'].iloc[-1]
                month_open_price = hist['Close'].iloc[0]
                high_price = hist['High'].max()
                low_price = hist['Low'].min()
                price_change = last_price - month_open_price
                percentage = (price_change / month_open_price) * 100
                trend = "Bullish (Up)" if last_price > month_open_price else "Bearish (Down)"
                
                news = stock.news[:3] if hasattr(stock, 'news') else []
                news_text = "\n".join([f"- {b['title']}" for b in news]) if news else "No recent news available."
                
                anim_placeholder.empty() 
                
                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.metric("Current Price", f"{last_price:,.2f}", f"{price_change:,.2f} ({percentage:.2f}%)")
                c_m2.metric("Resistance (High)", f"{high_price:,.2f}")
                c_m3.metric("Support (Low)", f"{low_price:,.2f}")
                
                st.caption("📍 Current Price Position (Support ↔ Resistance)")
                price_range = high_price - low_price
                percent_position = (last_price - low_price) / price_range if price_range > 0 else 0.5
                st.progress(float(max(0, min(1, percent_position))))
                
                with st.expander("📰 Current Market Sentiment (Latest News)", expanded=True):
                    st.write(news_text)
                st.line_chart(hist['Close'])
                
                summary_data = f"Ticker: {ticker_input}\nPrice: {last_price:.2f}\nSupport: {low_price:.2f}\nResistance: {high_price:.2f}\nTrend: {trend}\nNews:\n{news_text}"
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", "You are a professional stock analyst. Provide trend analysis, news impact, and safe ENTRY suggestions (if bullish). Use English."),
                    ("user", "Market Data:\n{data}")
                ])
                response = (prompt_template | llm).invoke({"data": summary_data})
                
                st.markdown(f'<div class="ai-card"><h4>🤖 FintechAI Analysis</h4>{response.content}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button("📥 Download Stock Report (.txt)", response.content, f"Report_{ticker_input}.txt", mime="text/plain")
                
        except Exception as e:
            anim_placeholder.empty()
            st.error(f"⚠️ Failed to generate AI analysis. Ensure your AMD server is ON! Error: {e}")

elif menu_choice == "PDF Report Analyzer":
    st.header("📄 Financial Report Scanner")
    st.markdown("The **Keyword Hunter** algorithm will select the most relevant pages from the Annual Report.")
    
    uploaded_file = st.file_uploader("Upload financial document (PDF)", type="pdf")
    user_question = st.text_input("What do you want to know from this report?", "Please provide a summary of profit and revenue from this document.")
    
    if uploaded_file and st.button("Start Document Breakdown", type="primary"):
        anim_placeholder = st.empty()
        with anim_placeholder.container():
            if lottie_thinking: st_lottie(lottie_thinking, height=150, key="loading_pdf")
            st.markdown("<h5 style='text-align:center; color:#00FFA3;'>Extracting and reading document...</h5>", unsafe_allow_html=True)
            
        try:
            pdf_reader = PdfReader(uploaded_file)
            teks_dokumen = ""
            kata_kunci = ["profit", "revenue", "risk", "prospect", "asset", "liability", "loss", "income", "laba", "pendapatan"]
            halaman_ditemukan = 0
            
            for i, page in enumerate(pdf_reader.pages):
                teks_halaman = page.extract_text()
                if teks_halaman and any(k in teks_halaman.lower() for k in kata_kunci):
                    teks_dokumen += f"--- PAGE {i+1} ---\n{teks_halaman}\n\n"
                    halaman_ditemukan += 1
                if halaman_ditemukan >= 15: break
            
            if halaman_ditemukan == 0:
                anim_placeholder.empty()
                st.warning("⚠️ Standard financial format not detected. Switching to General Extraction Mode...")
                total_pages = len(pdf_reader.pages)
                sampel_awal = list(range(min(3, total_pages)))
                sampel_tengah = list(range(max(3, total_pages//2), min(total_pages, (total_pages//2) + 3)))
                
                for i in sorted(list(set(sampel_awal + sampel_tengah))):
                    teks_dokumen += f"--- PAGE {i+1} ---\n{pdf_reader.pages[i].extract_text()}\n\n"
                
                prompt_aktif = ChatPromptTemplate.from_messages([
                    ("system", "You are a Professional Document Analyst. Summarize the text to answer the question. CRITICAL RULE: If the text is completely unrelated to business/finance, REJECT it by stating: 'The provided document is not suitable. Please upload a financial document.'"),
                    ("user", "Document:\n{dokumen}\n\nQuestion: {pertanyaan}")
                ])
            else:
                anim_placeholder.empty()
                st.success(f"Successfully extracted {halaman_ditemukan} crucial pages.")
                prompt_aktif = ChatPromptTemplate.from_messages([
                    ("system", "You are a Senior Financial Auditor. Answer the user's question accurately based ONLY on the provided text. Use bullet points."),
                    ("user", "Document:\n{dokumen}\n\nQuestion: {pertanyaan}")
                ])
                
            jawaban_pdf = (prompt_aktif | llm).invoke({"dokumen": teks_dokumen, "pertanyaan": user_question})
            
            st.markdown(f'<div class="ai-card"><h4>🤖 Auditor\'s Verdict</h4>{jawaban_pdf.content}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("📥 Download PDF Breakdown (.txt)", jawaban_pdf.content, "PDF_Breakdown.txt", mime="text/plain")

        except Exception as e:
            anim_placeholder.empty()
            st.error(f"⚠️ Failed to analyze PDF. Ensure your AMD server is ON! Error: {e}")

elif menu_choice == "Portfolio Advisor":
    st.header("💼 AI Portfolio Advisor")
    st.markdown("Enter your current stock positions to get an objective performance analysis and personalized action plan from our AI.")
    
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    
    with st.form("portfolio_form"):
        st.subheader("1. Enter Your Position")
        col1, col2, col3 = st.columns(3)
        with col1:
            ticker = st.text_input("Stock Ticker (e.g., AAPL, BRPT.JK)", "BRPT.JK")
        with col2:
            avg_price = st.number_input("Average Buy Price", min_value=1.0, value=4000.0, step=10.0)
        with col3:
            shares = st.number_input("Number of Lots / Shares", min_value=1, value=5, step=1)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("2. Select Your Risk Profile")
        risk_profile = st.select_slider(
            "What is your investment risk tolerance?",
            options=["Conservative (Low Risk)", "Moderate (Medium Risk)", "Aggressive (High Risk)"],
            value="Moderate (Medium Risk)"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_advisor = st.form_submit_button("Analyze My Portfolio", type="primary", use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    if submit_advisor:
        anim_placeholder = st.empty()
        with anim_placeholder.container():
            if lottie_thinking: st_lottie(lottie_thinking, height=150, key="loading_portfolio")
            st.markdown("<h5 style='text-align:center; color:#00FFA3;'>Auditing your portfolio...</h5>", unsafe_allow_html=True)
            
        try:
            saham = yf.Ticker(ticker)
            hist_1d = saham.history(period="1d") # Untuk harga hari ini
            hist_max = saham.history(period="max") # Untuk cek All Time High/Low
            
            if hist_1d.empty or hist_max.empty:
                anim_placeholder.empty()
                st.error("Ticker not found. Please check the symbol.")
            else:
                current_price = hist_1d['Close'].iloc[-1]
                
                # Cek All-Time High dan All-Time Low
                ath = hist_max['High'].max()
                atl = hist_max['Low'].min()
                
                is_indo = ticker.endswith(".JK")
                mata_uang = "Rp" if is_indo else "$"
                pengali_lembar = 100 if is_indo else 1 
                
                anim_placeholder.empty() 
                
                # --- VALIDASI HARGA HISTORIS ---
                if avg_price > ath or avg_price < atl:
                    st.warning(f"⚠️ **Anomaly Detected:** The average price you entered ({mata_uang} {avg_price:,.0f}) is outside historical bounds. The All-Time High for {ticker} is {mata_uang} {ath:,.0f} and the All-Time Low is {mata_uang} {atl:,.0f}. The analysis will continue, but please verify your input.")
                
                total_lembar = shares * pengali_lembar
                initial_capital = avg_price * total_lembar
                current_value = current_price * total_lembar
                pnl_amount = current_value - initial_capital
                pnl_percent = (pnl_amount / initial_capital) * 100 if initial_capital > 0 else 0
                
                status = "Floating Profit" if pnl_amount > 0 else "Floating Loss"
                
                st.subheader("📊 Position Summary")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Current Price", f"{mata_uang} {current_price:,.0f}")
                m2.metric("Total Investment", f"{mata_uang} {initial_capital:,.0f}")
                m3.metric("Current Value", f"{mata_uang} {current_value:,.0f}")
                m4.metric("Unrealized P/L", f"{mata_uang} {pnl_amount:,.0f}", f"{pnl_percent:.2f}%")
                
                st.divider()
                
                prompt_advisor = ChatPromptTemplate.from_messages([
                    ("system", """You are a highly skilled, objective Professional Financial Advisor. 
                    Analyze the user's current stock position. 
                    CRITICAL RULES:
                    1. You MUST tailor your advice based on the user's Risk Profile.
                    2. IF Position Status is 'Floating Loss' (minus percentage), you MUST NEVER recommend 'TAKE PROFIT'. You can only recommend HOLD, AVERAGE DOWN, or CUT LOSS.
                    3. IF Position Status is 'Floating Profit' (plus percentage), you MUST NEVER recommend 'CUT LOSS'.
                    4. Clearly state your final verdict: HOLD, CUT LOSS, AVERAGE DOWN, or TAKE PROFIT.
                    5. Provide a brief psychological and technical rationale.
                    6. Answer in professional English using bullet points."""),
                    ("user", f"""
                    Asset: {ticker}
                    User's Average Price: {mata_uang} {avg_price:,.0f}
                    Current Market Price: {mata_uang} {current_price:,.0f}
                    Position Status: {status} ({pnl_percent:.2f}%)
                    User's Risk Profile: {risk_profile}
                    
                    Give me your recommendation.""")
                ])
                
                jawaban_advisor = (prompt_advisor | llm).invoke({})
                
                st.markdown(f'<div class="ai-card"><h4>🤖 Advisor\'s Verdict</h4>{jawaban_advisor.content}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button("📥 Download Advice (.txt)", jawaban_advisor.content, f"Portfolio_Advice_{ticker}.txt", mime="text/plain")

        except Exception as e:
            anim_placeholder.empty()
            st.error(f"⚠️ Failed to generate AI analysis. Ensure your AMD server is ON! Error: {e}")
            
# --- FOOTER DISCLAIMER ---
st.markdown("---")
st.caption("""
**⚠️ Disclaimer:** FintechAI is an AI-powered experimental tool. All generated analysis, portfolio advice, and market predictions are for informational and educational purposes only. They do not constitute financial, investment, or trading advice. Always do your own research (DYOR) before making any investment decisions.
""")
            