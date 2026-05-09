import streamlit as st
import yfinance as yf
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pypdf import PdfReader
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="FintechAI - Dashboard", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# --- 2. LOTTIE ANIMATION FUNCTION ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Load "AI Thinking" animation
lottie_thinking = load_lottieurl("https://lottie.host/786bd49b-7cc2-4df7-873d-9d41315fc472/rJ4w2A61qK.json") 

# --- 3. AMD SERVER CONNECTION ---
@st.cache_resource
def init_llm():
    return ChatOpenAI(
        base_url="http://165.245.143.132:8000/v1", # ENSURE THIS IP IS CORRECT
        api_key="empty", 
        model="Qwen/Qwen2.5-1.5B-Instruct",
        max_tokens=1200
    )
llm = init_llm()

# --- 4. CSS INJECTION (HERO BANNER & AI CARD) ---
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
    <p class="app-subtitle">Autonomous Financial Analytics System with Edge GPU Computing</p>
    <div class="terminal-window">
        <div class="terminal-header"><div class="t-dot red"></div><div class="t-dot yellow"></div><div class="t-dot green"></div></div>
        <div class="terminal-body"><span class="cmd-user">root@amd-server:~#</span> ./start_fintech_engine.sh<br><span class="cmd-text">[INFO] Initializing Qwen-1.5B on MI300X... OK</span><br><span class="cmd-user">root@amd-server:~#</span> Awaiting command<span class="cursor"></span></div>
    </div>
</div>
"""
st.markdown(custom_css + hero_html, unsafe_allow_html=True)

# --- 5. SIDEBAR MENU ---
with st.sidebar:
    # 1. Display your landscape image bbtech.jpg
    try:
        # The use_container_width parameter will automatically adjust the image to the sidebar width
        st.image("bbtech.jpg", use_container_width=True)
    except:
        # If the image is not in the project folder, display a temporary message
        st.caption("*(bbtech.jpg image has not been placed in the project folder)*")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Trick to turn the Black AMD Logo White using CSS Filter
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/7/7c/AMD_Logo.svg" 
                 style="width: 120px; filter: brightness(0) invert(1);">
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # 3. Navigation Menu with new colors
    menu_choice = option_menu(
        menu_title=None, # Removed to keep it clean since the bbtech image is already present
        options=["Stock Analysis", "PDF Report Analyzer"],
        icons=["graph-up-arrow", "file-earmark-pdf"],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#00FFA3", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px 0px", "border-radius":"8px", "--hover-color": "#334155"},
            "nav-link-selected": {"background-color": "#1E293B", "color": "#00FFA3", "font-weight": "bold", "border-left": "4px solid #00FFA3"},
        }
    )

# --- 6. MAIN PAGE LOGIC ---

if menu_choice == "Stock Analysis":
    st.header("📊 Sentiment & Technical Analysis")
    
    # --- FUNGSI PENARIK DATA PASAR GLOBAL (Ditaruh sebelum blok UI) ---
@st.cache_data(ttl=300) # Cache 5 menit agar aplikasi tidak lambat/spamming request
def get_global_market_pulse():
    # Simbol resmi di Yahoo Finance
    tickers = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "BTC/USD": "BTC-USD",
        "Gold": "GC=F"
    }
    data = {}
    for name, symbol in tickers.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="2d") # Tarik data 2 hari untuk hitung persentase (+/-)
            if len(hist) >= 2:
                harga_sekarang = hist['Close'].iloc[-1]
                harga_kemarin = hist['Close'].iloc[-2]
                persentase = ((harga_sekarang - harga_kemarin) / harga_kemarin) * 100
                data[name] = {"val": harga_sekarang, "pct": persentase}
            else:
                data[name] = None
        except:
            data[name] = None # Jika error (misal internet mati), kembalikan None
    return data

# --- MINI MARKET DASHBOARD UI ---
st.markdown("##### 🌐 Global Market Pulse")

# Panggil fungsi penarik data
market_data = get_global_market_pulse()

m_col1, m_col2, m_col3, m_col4 = st.columns(4)

# Fungsi kecil untuk merender metrik agar kodenya tidak panjang
def render_metric(col, name, prefix=""):
    info = market_data.get(name)
    if info is not None:
        # Jika berhasil narik data, tampilkan angkanya
        val_str = f"{prefix}{info['val']:,.2f}"
        pct_str = f"{info['pct']:.2f}%"
        col.metric(label=name, value=val_str, delta=pct_str)
    else:
        # Jika gagal/error, tampilkan N/A tapi nama aset (label) tetap ada
        col.metric(label=name, value="N/A", delta="N/A", delta_color="off")

# Render ke 4 kolom
render_metric(m_col1, "S&P 500")
render_metric(m_col2, "NASDAQ")
render_metric(m_col3, "BTC/USD", prefix="$")
render_metric(m_col4, "Gold", prefix="$")

st.markdown("<br>", unsafe_allow_html=True) # Jarak kosong

# --- TRENDING TICKERS SUGGESTION ---
st.caption("🔥 **Trending today:** AAPL, NVDA, TSLA, MSFT, BBCA.JK")
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        ticker_input = st.text_input("Stock Ticker (e.g., BBCA.JK, AAPL):", "BBCA.JK")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True) # Spacer
        analyze_button = st.button("Run Analysis", type="primary", use_container_width=True)
        
    if analyze_button:
        anim_placeholder = st.empty()
        with anim_placeholder.container():
            if lottie_thinking: st_lottie(lottie_thinking, height=150, key="loading_stock")
            st.markdown("<h5 style='text-align:center; color:#00E676;'>Pulling market data and news sentiment...</h5>", unsafe_allow_html=True)
            
        try:
            stock = yf.Ticker(ticker_input)
            hist = stock.history(period="1mo")
            
            if hist.empty:
                anim_placeholder.empty()
                st.error("Stock data not found. Ensure the ticker is correct.")
            else:
                # Metrics Calculation
                last_price = hist['Close'].iloc[-1]
                month_open_price = hist['Close'].iloc[0]
                high_price = hist['High'].max()
                low_price = hist['Low'].min()
                price_change = last_price - month_open_price
                percentage = (price_change / month_open_price) * 100
                trend = "Bullish (Up)" if last_price > month_open_price else "Bearish (Down)"
                
                # Fetch News
                news = stock.news[:3] if hasattr(stock, 'news') else []
                news_text = "\n".join([f"- {b['title']}" for b in news]) if news else "No recent news available."
                
                anim_placeholder.empty() # Remove animation
                
                # Executive Dashboard UI
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Current Price", f"{last_price:.2f}", f"{price_change:.2f} ({percentage:.2f}%)")
                col_m2.metric("Resistance (High)", f"{high_price:.2f}")
                col_m3.metric("Support (Low)", f"{low_price:.2f}")
                
                # Progress Bar
                st.caption("📍 Current Price Position (Support ↔ Resistance)")
                price_range = high_price - low_price
                percent_position = (last_price - low_price) / price_range if price_range > 0 else 0.5
                st.progress(float(max(0, min(1, percent_position))))
                
                # News & Chart
                with st.expander("📰 Current Market Sentiment (Latest News)", expanded=True):
                    st.write(news_text)
                st.line_chart(hist['Close'])
                
                # AI Invocation
                summary_data = f"Ticker: {ticker_input}\nPrice: {last_price:.2f}\nSupport: {low_price:.2f}\nResistance: {high_price:.2f}\nTrend: {trend}\nNews:\n{news_text}"
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", "You are a professional stock analyst. Provide trend analysis, news impact, and safe ENTRY suggestions (if bullish). Use English."),
                    ("user", "Market Data:\n{data}")
                ])
                response = (prompt_template | llm).invoke({"data": summary_data})
                
                # Output Card
                st.markdown(f'<div class="ai-card"><h4>🤖 FintechAI Analysis</h4>{response.content}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button("📥 Download Stock Report (.txt)", response.content, f"Report_{ticker_input}.txt", mime="text/plain")
                
        except Exception as e:
            anim_placeholder.empty()
            st.error(f"An error occurred: {e}")

elif menu_choice == "PDF Report Analyzer":
    st.header("📄 Financial Report Scanner")
    st.markdown("The **Keyword Hunter** algorithm will select the most relevant pages from the Annual Report.")
    
    uploaded_file = st.file_uploader("Upload financial document (PDF)", type="pdf")
    user_question = st.text_input("What do you want to know from this report?", "Please provide a summary of profit and revenue from this document.")
    
    if uploaded_file and st.button("Start Document Breakdown", type="primary"):
        anim_placeholder = st.empty()
        with anim_placeholder.container():
            if lottie_thinking: st_lottie(lottie_thinking, height=150, key="loading_pdf")
            st.markdown("<h5 style='text-align:center; color:#00E676;'>Extracting and reading document...</h5>", unsafe_allow_html=True)
            
        try:
            pdf_reader = PdfReader(uploaded_file)
            document_text = ""
            keywords = ["profit", "revenue", "income", "risk", "prospect", "asset", "liability", "loss"]
            pages_found = 0
            
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text and any(k in page_text.lower() for k in keywords):
                    document_text += f"--- PAGE {i+1} ---\n{page_text}\n\n"
                    pages_found += 1
                if pages_found >= 15: break
            
            # Plan B Logic (Fallback)
            if pages_found == 0:
                anim_placeholder.empty()
                st.warning("⚠️ Document does not use standard financial formatting. Switching to General Extraction Mode...")
                
                total_pages = len(pdf_reader.pages)
                early_sample = list(range(min(3, total_pages)))
                mid_sample = list(range(max(3, total_pages//2), min(total_pages, (total_pages//2) + 3)))
                
                for i in sorted(list(set(early_sample + mid_sample))):
                    document_text += f"--- PAGE {i+1} ---\n{pdf_reader.pages[i].extract_text()}\n\n"
                
                active_prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are a Professional Document Analyst. Create a summary to answer the question.
                    CRITICAL RULE: If the text does not discuss business/finance/economics at all, REJECT by answering: "The provided document is inappropriate. Please upload a financially related document." """),
                    ("user", "Document:\n{document}\n\nQuestion: {question}")
                ])
            else:
                anim_placeholder.empty()
                st.success(f"Successfully extracted {pages_found} crucial pages.")
                active_prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are a Senior Financial Auditor. Answer the user's question accurately based on the attached text. Use bullet points."),
                    ("user", "Document:\n{document}\n\nQuestion: {question}")
                ])
                
            # AI Invocation
            pdf_response = (active_prompt | llm).invoke({"document": document_text, "question": user_question})
            
            # Output Card
            st.markdown(f'<div class="ai-card"><h4>🤖 FintechAI Auditor Response</h4>{pdf_response.content}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("📥 Download PDF Breakdown Result (.txt)", pdf_response.content, "PDF_Breakdown_Result.txt", mime="text/plain")

        except Exception as e:
            anim_placeholder.empty()
            st.error(f"An error occurred while reading the PDF: {e}")
            
# --- FOOTER DISCLAIMER ---
st.markdown("---")
st.caption("""
**⚠️ Disclaimer:** FintechAI is an AI-powered experimental tool. All generated analysis, portfolio advice, and market predictions are for informational and educational purposes only. They do not constitute financial, investment, or trading advice. Always do your own research (DYOR) before making any investment decisions.
""")
            