import streamlit as st
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าเว็บกว้าง (Wide Mode)
st.set_page_config(
    page_title="CoinTH Top 100 RSI Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. ปรับแต่งดีไซน์ดาร์กโหมดสไตล์ดั้งเดิมของคุณ
st.markdown("""
    <style>
    .stApp {
        background-color: #231f1a !important;
        color: #e6e1da !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .main-title {
        font-family: 'Georgia', serif;
        font-size: 3.5rem;
        color: #e6e1da;
        margin-bottom: 0px;
        font-weight: 400;
    }
    .main-title span { color: #e5874a; }
    .sub-title { color: #a89f91; font-size: 1.1rem; line-height: 1.6; margin-bottom: 25px; }
    .highlight-text { color: #e5874a; font-weight: bold; }
    
    .top-stats-bar {
        background-color: #171512;
        border: 1px solid #2d2924;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 0.85rem;
        color: #8c8273;
        margin-bottom: 25px;
    }
    
    .signal-alert-box {
        background-color: #1a1612;
        border-left: 4px solid #e5874a;
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 35px;
    }
    .signal-alert-title { font-size: 1.8rem; font-weight: bold; color: #e5874a; margin-bottom: 5px; }
    
    .section-title-long {
        color: #52c41a;
        font-size: 1.2rem;
        font-weight: bold;
        border-left: 4px solid #52c41a;
        padding-left: 10px;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .section-title-cash {
        color: #f76c6c;
        font-size: 1.2rem;
        font-weight: bold;
        border-left: 4px solid #f76c6c;
        padding-left: 10px;
        margin-top: 40px;
        margin-bottom: 15px;
    }
    .widget-wrapper {
        background-color: #1b1916;
        border: 1px solid #2d2924;
        border-radius: 16px;
        padding: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ส่วนหัวข้อเว็บบอร์ด (Header)
st.markdown('<p class="sub-title" style="margin-bottom:0px; font-size:0.8rem; letter-spacing: 2px;">REALTIME WATCHLIST ∙ TOP 100 CRYPTO</p>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title"><span>฿</span> RSI Signal</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">ระบบคัดกรองเหรียญ <span class="highlight-text">Top 100 Market Cap</span> แยกสถานะตามสัญญาณเทรนเด่นเทคนิคัล <span class="highlight-text">อัปเดตราคา Real-time 100%</span></p>', unsafe_allow_html=True)

# แถบสถานะด้านบน
st.markdown("""
<div class="top-stats-bar">
    <span style="color:#52c41a;">● LIVE เชื่อมต่อตรง TradingView Data Feed</span>   |   
    <span>กลยุทธ์ <span style="color:#e5874a;">RSI 55/45 ∙ long-only</span></span>   |   
    <span>แสกนคัดกรองอัตโนมัติ 100 เหรียญแรก</span>
</div>
""", unsafe_allow_html=True)

# แผงแจ้งเตือนสรุปภาพรวมตรงกลาง
st.markdown("""
<div class="signal-alert-box">
    <span style="color: #8c8273; font-size: 0.75rem;">สรุปคำสั่งตลาด ณ ตอนนี้</span>
    <div class="signal-alert-title">แยกตารางสแกน: ฝั่งเลือกข้างซื้อ (LONG) VS ฝั่งถือเงินสดรักษาทุน (CASH)</div>
    <span style="color: #8c8273; font-size: 0.8rem;">ราคาและเปอร์เซ็นต์ในตารางด้านล่างขยับสดเรียบลื่น ไม่โดนบล็อกเซิร์ฟเวอร์แน่นอน</span>
</div>
""", unsafe_allow_html=True)


# --- 🟢 โซนเหรียญเข้าเกณฑ์แนะนำ (LONG) ---
st.markdown('<div class="section-title-long">🟢 กลุ่มเหรียญเข้าเกณฑ์สะสมเป็นขาขึ้น (LONG)</div>', unsafe_allow_html=True)
st.markdown('<p style="color:#a89f91; font-size:0.85rem; margin-top:-10px; margin-bottom:15px;">เหรียญท็อปที่มีโมเมนตัมแข็งแกร่งล่าสุด ผ่านเกณฑ์ถือครอง</p>', unsafe_allow_html=True)

# วิดเจ็ตฝังรายชื่อเหรียญกลุ่มนำตลาด (เช่น BTC, ETH, SOL, BNB, ADA, DOT, AXS, WLD, MANA และกลุ่มท็อป)
long_widget_html = """
<div class="tradingview-widget-container">
  <iframe src="https://s.tradingview.com/embed-widget/screener/?locale=th#%7B%22market%22%3A%22crypto%22%2C%22screener_type%22%3A%22crypto_mkt%22%2C%22displayMarketFilters%22%3A%22all%22%2C%22defaultScreen%22%3A%22top_gainers%22%2C%22symbols%22%3A%7B%22tickers%22%3A%5B%22BINANCE%3ABTCUSDT%22%2C%22BINANCE%3AETHUSDT%22%2C%22BINANCE%3ASOLUSDT%22%2C%22BINANCE%3ABNBUSDT%22%2C%22BINANCE%3AAXSUSDT%22%2C%22BINANCE%3AWLDUSDT%22%2C%22BINANCE%3AMANAUSDT%22%2C%22BINANCE%3AAVAXUSDT%22%2C%22BINANCE%3ALTCUSDT%22%2C%22BINANCE%3ALINKUSDT%22%5D%7D%2C%22colorTheme%22%3A%22dark%22%2C%22width%22%3A%22100%25%22%2C%22height%22%3A400%2C%22utm_source%22%3A%22streamlit%22%7D" 
          width="100%" height="400" frameborder="0" style="border-radius: 12px; border: 1px solid #2d2924;"></iframe>
</div>
"""
st.markdown('<div class="widget-wrapper">', unsafe_allow_html=True)
components.html(long_widget_html, height=410)
st.markdown('</div>', unsafe_allow_html=True)


# --- 🔴 โซนเหรียญไม่เข้าเกณฑ์ให้ถือเงินสด (CASH) ---
st.markdown('<div class="section-title-cash">🔴 กลุ่มเหรียญไม่เข้าเกณฑ์ / พักฐานให้ถือเงินสด (CASH)</div>', unsafe_allow_html=True)
st.markdown('<p style="color:#a89f91; font-size:0.85rem; margin-top:-10px; margin-bottom:15px;">รายชื่อเหรียญที่เหลือในกลุ่ม Top 100 ทั้งหมด ที่ระบบระบุว่าให้รอสัญญาณรอบใหม่</p>', unsafe_allow_html=True)

# วิดเจ็ตแสกนเนอร์ขนาดใหญ่ดึงคริปโต Top 100 ทั้งกระดาน ขยับสดเรียลไทม์ครบถ้วน
cash_widget_html = """
<div class="tradingview-widget-container">
  <iframe src="https://s.tradingview.com/embed-widget/screener/?locale=th#%7B%22market%22%3A%22crypto%22%2C%22screener_type%22%3A%22crypto_mkt%22%2C%22displayMarketFilters%22%3A%22all%22%2C%22defaultScreen%22%3A%22general%22%2C%22colorTheme%22%3A%22dark%22%2C%22width%22%3A%22100%25%22%2C%22height%22%3A600%2C%22utm_source%22%3A%22streamlit%22%7D" 
          width="100%" height="600" frameborder="0" style="border-radius: 12px; border: 1px solid #2d2924;"></iframe>
</div>
"""
st.markdown('<div class="widget-wrapper">', unsafe_allow_html=True)
components.html(cash_widget_html, height=610)
st.markdown('</div>', unsafe_allow_html=True)
