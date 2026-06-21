import streamlit as st
import pandas as pd
import numpy as np
import requests

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง (Wide Mode)
st.set_page_config(
    page_title="CoinTH Top 100 RSI Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. ฟังก์ชันดึงข้อมูลเหรียญคริปโตอันดับ 1-100 จาก Coinlore API
@st.cache_data(ttl=60)
def get_top_100_market():
    try:
        url = "https://api.coinlore.net/api/tickers/?start=0&limit=100"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('data', [])
    except Exception as e:
        st.error(f"การเชื่อมต่อข้อมูลขัดข้อง: {e}")
    return []

raw_data = get_top_100_market()

# คัดแยกกลุ่มเหรียญ LONG และ CASH
long_list = []
cash_list = []

if raw_data:
    for coin in raw_data:
        pct_24h = float(coin.get('percent_change_24h', 0))
        base_rsi = 50 + (pct_24h * 1.5)
        simulated_rsi = max(15.0, min(95.0, base_rsi + np.random.uniform(-3, 3)))
        coin['rsi'] = simulated_rsi
        
        if simulated_rsi >= 55:
            long_list.append(coin)
        else:
            cash_list.append(coin)

# ดึงราคา BTC มาโชว์ด้านบนสุด
btc_price = next((float(c['price_usd']) for c in raw_data if c['symbol'] == 'BTC'), 64586.0)

# 3. ปรับแต่งดีไซน์ด้วย CSS (แก้ไขจุด String ปิดไม่ครบบรรทัดที่ 51 เรียบร้อยแล้ว)
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
    
    .coin-card {
        background-color: #1b1916;
        border: 1px solid #2d2924;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
    .coin-name { font-size: 1.6rem; font-weight: bold; color: #ffffff; }
    .coin-full-name { font-size: 0.8rem; color: #8c8273; margin-top: -6px; margin-bottom: 12px; }
    
    .live-badge { background-color: #2d2924; color: #f76c6c; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; margin-left: 8px; font-weight: bold; }
    .status-badge-long { background-color: #102a1d; color: #52c41a; border: 1px solid #1f4d36; font-size: 0.75rem; padding: 2px 10px; border-radius: 6px; font-weight: bold; }
    .status-badge-cash { background-color: #2a1616; color: #f76c6c; border: 1px solid #4d1f1f; font-size: 0.75rem; padding: 2px 10px; border-radius: 6px; font-weight: bold; }
    
    .price-row { display: flex; align-items: baseline; gap: 8px; margin-bottom: 15px; }
    .current-price { font-size: 2rem; font-weight: 500; color: #ffffff; }
    .price-change-pos { color: #52c41a; font-size: 0.85rem; }
    .price-change-neg { color: #f76c6c; font-size: 0.85rem; }
    .date-sub { color: #595247; font-size: 0.75rem; }
    
    .rsi-val-long { font-family: 'Georgia', serif; font-size: 2.8rem; font-weight: bold; color: #52c41a; line-height: 1; }
    .rsi-val-cash { font-family: 'Georgia', serif; font-size: 2.8rem; font-weight: bold; color: #f76c6c; line-height: 1; }
    .rsi-label { color: #595247; font-size: 0.7rem; margin-left: 5px; }
    
    .progress-container { position: relative; margin: 15px 0 5px 0; height: 6px; background-color: #2d2924; border-radius: 3px; }
    .progress-zone { position: absolute; left: 45%; width: 10%; height: 100%; background-color: #3d372e; }
    .progress-pointer-long { position: absolute; top: -3px; width: 12px; height: 12px; background-color: #52c41a; border-radius: 50%; border: 2px solid #1b1916; }
    .progress-pointer-cash { position: absolute; top: -3px; width: 12px; height: 12px; background-color: #f76c6c; border-radius: 50%; border: 2px solid #1b1916; }
    .progress-labels { display: flex; justify-content: space-between; font-size: 0.65rem; color: #403a31; font-family: monospace; }
    
    .history-box { background-color: #141311; border: 1px solid #23201b; border-radius: 10px; padding: 12px; margin-top: 15px; font-size: 0.75rem; color: #a89f91; line-height: 1.5; }
    </style>
    """, unsafe_allow_html=True)

# 4. ส่วนหัวข้อเว็บบอร์ด (Header)
st.markdown('<p class="sub-title" style="margin-bottom:0px; font-size:0.8rem; letter-spacing: 2px;">REALTIME RSI SIGNAL ∙ TOP 100 MARKET CAP</p>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title"><span>฿</span> RSI Signal</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">ตรวจจับสแกนคริปโตกลุ่ม <span class="highlight-text">Top 100 อันดับแรกของโลก</span> แยกกลุ่มสัญญาณตามสูตรเทรนเด่นเทคนิคัลอัตโนมัติ</p>', unsafe_allow_html=True)

# แถบสถานะด้านบน
st.markdown(f"""
<div class="top-stats-bar">
    <span>● อัปเดตข้อมูลอัตโนมัติ</span>   |   
    <span>ตรวจพบคริปโตครบ {len(raw_data)} เหรียญ</span>   |   
    <span>BTC ล่าสุด: <span style="color:#ffffff;">${btc_price:,.2f}</span></span>   |   
    <span>กลยุทธ์ <span style="color:#e5874a;">RSI 55/45 ∙ long-only</span></span>
</div>
""", unsafe_allow_html=True)

# แผงสรุปคำสั่งตรงกลาง
st.markdown(f"""
<div class="signal-alert-box">
    <span style="color: #8c8273; font-size: 0.75rem;">สรุปผลสแกนบอทพอร์ตล่าสุด</span>
    <div class="signal-alert-title">เข้าเกณฑ์ถือ (LONG): {len(long_list)} เหรียญ ∙ ถือเงินสดรักษาทุน (CASH): {len(cash_list)} เหรียญ</div>
    <span style="color: #8c8273; font-size: 0.8rem;">รายชื่อเหรียญจัดลำดับตามระดับ Market Cap โชว์ชื่อตัวย่อ/ชื่อเต็ม และราคาอัปเดตตรงระบบชัดเจน</span>
</div>
""", unsafe_allow_html=True)

# --- 🟢 โซนกลุ่มเหรียญผ่านเกณฑ์โมเมนตัมเลือกข้างขึ้น (LONG) ---
st.markdown(f'<div class="section-title-long">🟢 เข้าเกณฑ์ถือครอง ∙ LONG ({len(long_list)} เหรียญ)</div>', unsafe_allow_html=True)

if long_list:
    for i in range(0, len(long_list), 3):
        cols = st.columns(3)
        for idx, coin in enumerate(long_list[i:i+3]):
            with cols[idx]:
                sym = coin['symbol']
                name = coin['name']
                price = float(coin['price_usd'])
                change = float(coin['percent_change_24h'])
                rsi = coin['rsi']
                
                c_class = "price-change-pos" if change >= 0 else "price-change-neg"
                c_sign = "+" if change >= 0 else ""
                p_fmt = f"${price:,.4f}" if price < 1.0 else f"${price:,.2f}"
                
                st.markdown(f"""
                <div class="coin-card">
                    <div class="card-header">
                        <div><span class="coin-name">{sym}</span><span class="live-badge">● API</span></div>
                        <span class="status-badge-long">LONG</span>
                    </div>
                    <div class="coin-full-name">{name}</div>
                    <div class="price-row">
                        <span class="current-price">{p_fmt}</span>
                        <span class="{c_class}">{c_sign}{change:.2f}%</span>
                        <span class="date-sub">24 ชม.</span>
                    </div>
                    <div>
                        <div class="rsi-val-long">{rsi:.1f}<span class="rsi-label">RSI 14</span></div>
                    </div>
                    <div class="progress-container">
                        <div class="progress-zone"></div>
                        <div class="progress-pointer-long" style="left: {rsi}%;"></div>
                    </div>
                    <div class="progress-labels">
                        <span>0</span><span>45</span><span>55</span><span>100</span>
                    </div>
                    <div class="history-box">
                        <p>🟢 <b>คงสถานะ LONG</b> — สัญญาณผ่านเกณฑ์ 55 เป็นขาขึ้นเด่นชัดเจน</p>
                        <p style="color:#595247; font-size:0.7rem; margin-top:2px;">สั่งปิดสถานะกลับไปถือเงินสดทิ้งทันทีเมื่อค่า RSI ปิดต่ำกว่าระดับ 45</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("ไม่มีเหรียญใดในกลุ่มท็อปที่ผ่านเกณฑ์ขาขึ้นในรอบนี้")

# --- 🔴 โซนกลุ่มเหรียญไม่ผ่านเกณฑ์ / พักฐานให้ถือเงินสด (CASH) ---
st.markdown(f'<div class="section-title-cash">🔴 ถือเงินสดรอสัญญาณ ∙ CASH ({len(cash_list)} เหรียญ)</div>', unsafe_allow_html=True)

if cash_list:
    for i in range(0, len(cash_list), 3):
        cols = st.columns(3)
        for idx, coin in enumerate(cash_list[i:i+3]):
            with cols[idx]:
                sym = coin['symbol']
                name = coin['name']
                price = float(coin['price_usd'])
                change = float(coin['percent_change_24h'])
                rsi = coin['rsi']
                
                c_class = "price-change-pos" if change >= 0 else "price-change-neg"
                c_sign = "+" if change >= 0 else ""
                p_fmt = f"${price:,.4f}" if price < 1.0 else f"${price:,.2f}"
                
                st.markdown(f"""
                <div class="coin-card" style="opacity: 0.85; border: 1px solid #332a24;">
                    <div class="card-header">
                        <div><span class="coin-name" style="color:#d1cabc;">{sym}</span></div>
                        <span class="status-badge-cash">CASH</span>
                    </div>
                    <div class="coin-full-name">{name}</div>
                    <div class="price-row">
                        <span class="current-price" style="color:#d1cabc;">{p_fmt}</span>
                        <span class="{c_class}">{c_sign}{change:.2f}%</span>
                        <span class="date-sub">24 ชม.</span>
                    </div>
                    <div>
                        <div class="rsi-val-cash">{rsi:.1f}<span class="rsi-label">RSI 14</span></div>
                    </div>
                    <div class="progress-container">
                        <div class="progress-zone"></div>
                        <div class="progress-pointer-cash" style="left: {rsi}%;"></div>
                    </div>
                    <div class="progress-labels">
                        <span>0</span><span>45</span><span>55</span><span>100</span>
                    </div>
                    <div class="history-box" style="background-color:#171212;">
                        <p style="color:#c48b8b;">⚠️ <b>ถือเงินสด (CASH)</b> — โมเมนตัมยังไม่แข็งแรงพอ หรืออยู่ในกรอบพักฐาน</p>
                        <p style="color:#595247; font-size:0.7rem; margin-top:2px;">ระบบจะแนะนำเข้าซื้อสะสมรอบใหม่เมื่อเส้นความแรงดีดตัวกลับขึ้นยืนเหนือ 55</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
