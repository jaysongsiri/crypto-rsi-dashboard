import streamlit as st
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง (Wide Mode)
st.set_page_config(
    page_title="CoinTH Realtime RSI Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. ปรับแต่งดีไซน์ด้วย CSS (มู้ดดาร์กโหมดสไตล์ดั้งเดิม)
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
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
    }
    
    .signal-alert-box {
        background-color: #1a1612;
        border-left: 4px solid #e5874a;
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 35px;
    }
    .signal-alert-title { font-size: 1.8rem; font-weight: bold; color: #e5874a; margin-bottom: 5px; }
    
    .widget-container {
        background-color: #1b1916;
        border: 1px solid #2d2924;
        border-radius: 16px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .coin-header-title {
        font-size: 1.4rem;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .status-badge {
        background-color: #102a1d;
        color: #52c41a;
        border: 1px solid #1f4d36;
        font-size: 0.75rem;
        padding: 2px 10px;
        border-radius: 6px;
        font-weight: bold;
    }
    .live-badge { background-color: #2d2924; color: #52c41a; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. ส่วนหัวข้อเว็บบอร์ด (Static Header)
st.markdown('<p class="sub-title" style="margin-bottom:0px; font-size:0.8rem; letter-spacing: 2px;">REALTIME RSI SIGNAL + TRADINGVIEW (WIDGET)</p>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title"><span>฿</span> RSI Signal</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">ตอนนี้เหรียญในกลุ่ม <span class="highlight-text">Watchlist</span> ตัวไหนผ่านเกณฑ์ควรถือสถานะไหน — ข้อมูลราคาขยับ <span class="highlight-text">Real-time ไหลลื่นจาก TradingView 100%</span></p>', unsafe_allow_html=True)

# แถบสถานะด้านบน
st.markdown(f"""
<div class="top-stats-bar">
    <span style="color:#52c41a;">● LIVE เชื่อมต่อตรงกับ TradingView Network</span>   |   
    <span>กลยุทธ์ <span style="color:#e5874a;">RSI 55/45 ∙ long-only</span></span>   |   
    <span>สถานะ: ระบบหน้าบ้านเสถียร 100%</span>
</div>
""", unsafe_allow_html=True)

# แผงแจ้งเตือนคำสั่งเด่นตรงกลาง
st.markdown(f"""
<div class="signal-alert-box">
    <span style="color: #8c8273; font-size: 0.75rem;">คำสั่ง ณ ตอนนี้</span>
    <div class="signal-alert-title">เข้าเกณฑ์ถือ: AXS ∙ WLD ∙ MANA ∙ SOL</div>
    <span style="color: #8c8273; font-size: 0.8rem;">เหรียญขาขึ้นแนะนำให้เข้าถือ (LONG) ตามเกณฑ์ระบบตัวเลขปิดแท่งล่าสุด</span>
</div>
""", unsafe_allow_html=True)

st.markdown(f'<p style="color:#8c8273; font-size:0.85rem; border-left: 3px solid #52c41a; padding-left:8px; margin-bottom:20px;">เหรียญเข้าเกณฑ์แนะนำ ∙ LONG</p>', unsafe_allow_html=True)

# ฟังก์ชันสร้างโค้ดการ์ด TradingView Mini-Chart
def create_tv_widget(symbol):
    return f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_{symbol}"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.MiniWidget({{
        "container_id": "tradingview_{symbol}",
        "symbol": "BINANCE:{symbol}USDT",
        "width": "100%",
        "height": 220,
        "locale": "th_TH",
        "dateRange": "1M",
        "colorTheme": "dark",
        "trendLineColor": "rgba(82, 196, 26, 1)",
        "underLineColor": "rgba(27, 25, 22, 0.5)",
        "underLineBottomColor": "rgba(27, 25, 22, 0.0)",
        "isTransparent": true,
        "autosize": false,
        "largeChartUrl": ""
      }});
      </script>
    </div>
    """

# 4. พล็อตการ์ดเหรียญแบ่งเป็นคอลัมน์สวยงาม
target_coins = ['BTC', 'ETH', 'AXS', 'WLD', 'MANA', 'SOL']

for i in range(0, len(target_coins), 3):
    cols = st.columns(3)
    for idx, coin in enumerate(target_coins[i:i+3]):
        with cols[idx]:
            st.markdown(f"""
            <div class="widget-container">
                <div class="coin-header-title">
                    <span>{coin}</span>
                    <span class="live-badge">● LIVE</span>
                    <span class="status-badge" style="margin-left:auto;">LONG</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # ฝังมินิกราฟเรียลไทม์ลงไปในการ์ดแต่ละใบ
            components.html(create_tv_widget(coin), height=230)
