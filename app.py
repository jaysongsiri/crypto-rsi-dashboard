import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง (Wide Mode)
st.set_page_config(
    page_title="CoinTH CAGR > 20% RSI Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. ฟังก์ชันคำนวณ RSI 14 ของจริง
def calculate_rsi(df, length=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# 3. ฟังก์ชันรัน Backtest หาค่า CAGR และสถานะปัจจุบันของจริง (ย้อนหลัง 3 ปี)
@st.cache_data(ttl=3600)  # แคชข้อมูลไว้ 1 ชม. เพื่อความรวดเร็วในการโหลดหน้าเว็บ
def backtest_rsi_strategy(ticker_symbol, name):
    try:
        # ดึงข้อมูลย้อนหลัง 3 ปี เพื่อมาหา CAGR
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3*365)
        
        df = yf.download(ticker_symbol, start=start_date, end=end_date, progress=False)
        if df.empty or len(df) < 50:
            return None
            
        df['RSI'] = calculate_rsi(df)
        df.dropna(inplace=True)
        
        # เริ่มจำลองการเทรด
        position = 0  # 0 = Cash, 1 = Long
        entry_price = 0
        total_return = 1.0 # เงินต้นสมมติ 1.0 (100%)
        
        for i in range(len(df)):
            rsi_val = df['RSI'].iloc[i]
            close_price = df['Close'].iloc[i]
            
            # เงื่อนไขเข้าซื้อ (Long)
            if position == 0 and rsi_val > 55:
                position = 1
                entry_price = close_price
            # เงื่อนไขขาย (Cash)
            elif position == 1 and rsi_val < 45:
                position = 0
                trade_return = close_price / entry_price
                total_return *= trade_return
                
        # ถ้าจังหวะปัจจุบันยังถืออยู่ ให้คิดกำไร unrealized ด้วย
        if position == 1:
            trade_return = df['Close'].iloc[-1] / entry_price
            current_total_return = total_return * trade_return
        else:
            current_total_return = total_return
            
        # คำนวณค่า CAGR (ทบต้นต่อปี ย้อนหลัง 3 ปี)
        years = 3.0
        cagr = (current_total_return ** (1.0 / years) - 1.0) * 100
        
        # ข้อมูลแท่งปัจจุบัน (Live)
        latest_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        price_change_pct = ((latest_price - prev_price) / prev_price) * 100
        latest_rsi = df['RSI'].iloc[-1]
        
        # ตรวจสอบสถานะปัจจุบันของแท่งล่าสุด
        current_status = "LONG" if latest_rsi > 55 or (position == 1 and latest_rsi >= 45) else "CASH"
        
        return {
            'symbol': ticker_symbol.replace('-USD', ''),
            'name': name,
            'price': float(latest_price),
            'change': float(price_change_pct),
            'rsi': float(latest_rsi),
            'cagr': float(cagr),
            'status': current_status
        }
    except:
        return None

# รายชื่อเหรียญหลักในตลาดที่จะนำมาสแกนคัดกรอง
watchlist = {
    'BTC-USD': 'Bitcoin', 'ETH-USD': 'Ethereum', 'SOL-USD': 'Solana', 
    'BNB-USD': 'BNB', 'ADA-USD': 'Cardano', 'XRP-USD': 'Ripple',
    'DOT-USD': 'Polkadot', 'AVAX-USD': 'Avalanche', 'LINK-USD': 'Chainlink',
    'LTC-USD': 'Litecoin', 'UNI-USD': 'Uniswap', 'NEAR-USD': 'NEAR Protocol',
    'APT-USD': 'Aptos', 'OP-USD': 'Optimism', 'RENDER-USD': 'Render Token'
}

# รันระบบแบคเทสคัดกรองเหรียญทั้งหมดใน Watchlist
scanned_coins = []
with st.spinner('⚙️ กำลังรัน Backtest สแกนหาเหรียญที่เปิดกลยุทธ์แล้ว CAGR > 20%...'):
    for ticker, name in watchlist.items():
        res = backtest_rsi_strategy(ticker, name)
        if res is not None:
            scanned_coins.append(res)

# กรองเฉพาะตัวที่ผ่านเกณฑ์ CAGR > 20% เท่านั้นตามคำสั่งของคุณ!
filtered_coins = [c for c in scanned_coins if c['cagr'] > 20.0]

# แยกกลุ่ม LONG และ CASH จากตัวที่ผ่านเกณฑ์แล้ว
long_list = [c for c in filtered_coins if c['status'] == "LONG"]
cash_list = [c for c in filtered_coins if c['status'] == "CASH"]

# 4. ปรับแต่งดีไซน์ด้วย CSS ดาร์กโหมดหรูหรา
st.markdown("""
    <style>
    .stApp { background-color: #231f1a !important; color: #e6e1da !important; font-family: 'Helvetica Neue', sans-serif; }
    .main-title { font-family: 'Georgia', serif; font-size: 3.5rem; color: #e6e1da; margin-bottom: 0px; font-weight: 400; }
    .main-title span { color: #e5874a; }
    .sub-title { color: #a89f91; font-size: 1.1rem; line-height: 1.6; margin-bottom: 25px; }
    .highlight-text { color: #e5874a; font-weight: bold; }
    
    .top-stats-bar { background-color: #171512; border: 1px solid #2d2924; border-radius: 8px; padding: 10px 20px; font-size: 0.85rem; color: #8c8273; margin-bottom: 25px; display: flex; flex-wrap: wrap; gap: 15px; }
    .signal-alert-box { background-color: #1a1612; border-left: 4px solid #e5874a; border-radius: 6px; padding: 20px; margin-bottom: 35px; }
    .signal-alert-title { font-size: 1.8rem; font-weight: bold; color: #e5874a; margin-bottom: 5px; }
    
    .section-title-long { color: #52c41a; font-size: 1.2rem; font-weight: bold; border-left: 4px solid #52c41a; padding-left: 10px; margin-top: 20px; margin-bottom: 15px; }
    .section-title-cash { color: #f76c6c; font-size: 1.2rem; font-weight: bold; border-left: 4px solid #f76c6c; padding-left: 10px; margin-top: 40px; margin-bottom: 15px; }
    
    .coin-card { background-color: #1b1916; border: 1px solid #2d2924; border-radius: 16px; padding: 24px; margin-bottom: 20px; }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
    .coin-name { font-size: 1.6rem; font-weight: bold; color: #ffffff; }
    .coin-full-name { font-size: 0.8rem; color: #8c8273; margin-top: -6px; margin-bottom: 12px; }
    
    .cagr-badge { background-color: #2b2214; color: #e5874a; font-size: 0.75rem; padding: 3px 8px; border-radius: 6px; border: 1px solid #4a371e; font-weight: bold; }
    .status-badge-long { background-color: #102a1d; color: #52c41a; border: 1px solid #1f4d36; font-size: 0.75rem; padding: 2px 10px; border-radius: 6px; font-weight: bold; }
    .status-badge-cash { background-color: #2a1616; color: #f76c6c; border: 1px solid #4d1f1f; font-size: 0.75rem; padding: 2px 10px; border-radius: 6px; font-weight: bold; }
    
    .price-row { display: flex; align-items: baseline; gap: 8px; margin-bottom: 15px; }
    .current-price { font-size: 2rem; font-weight: 500; color: #ffffff; }
    .price-change-pos { color: #52c41a; font-size: 0.85rem; }
    .price-change-neg { color: #f76c6c; font-size: 0.85rem; }
    
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

# 5. ส่วนหัวข้อเว็บบอร์ด (Header)
st.markdown('<p class="sub-title" style="margin-bottom:0px; font-size:0.8rem; letter-spacing: 2px;">REALTIME BACKTEST SCANNER</p>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title"><span>฿</span> RSI Signal</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">ระบบคัดกรองเหรียญเฉพาะที่ผ่านเกณฑ์ <span class="highlight-text">CAGR > 20%</span> จากการทดสอบย้อนหลัง 3 ปี ด้วยกลยุทธ์ <span class="highlight-text">RSI 55/45 Long-Only</span> ของจริง</p>', unsafe_allow_html=True)

# แถบสถานะด้านบน
st.markdown(f"""
<div class="top-stats-bar">
    <span>● คำนวณผลลัพธ์ผ่าน Backtest Engine สำเร็จ</span>   |   
    <span>คัดเลือกเหลือเฉพาะตัวที่ทำกำไรทบต้นเกิน 20% ต่อปี</span>   |   
    <span>กลยุทธ์: แท่งปิดวันรายวัน (Daily)</span>
</div>
""", unsafe_allow_html=True)

# แผงสรุปคำสั่งตรงกลาง
st.markdown(f"""
<div class="signal-alert-box">
    <span style="color: #8c8273; font-size: 0.75rem;">ผลลัพธ์ตัวกรองระบบคัดเกรดชั้นดี</span>
    <div class="signal-alert-title">ผ่านเกณฑ์ CAGR > 20%: ทั้งหมด {len(filtered_coins)} เหรียญ (จาก {len(scanned_coins)} เหรียญที่สแกน)</div>
    <span style="color: #8c8273; font-size: 0.8rem;">ตัวที่ไม่ผ่านเกณฑ์หรือรันระบบแล้วได้ผลตอบแทนไม่คุ้มค่าความเสี่ยงจะถูกตัดออกจากแดชบอร์ดโดยอัตโนมัติ</span>
</div>
""", unsafe_allow_html=True)


# --- 🟢 โซนเหรียญผ่านเกณฑ์และมีสถานะปัจจุบันเป็น LONG ---
st.markdown(f'<div class="section-title-long">🟢 ผ่านเกณฑ์ CAGR > 20% และสถานะปัจจุบันเป็นเข้าถือครอง ∙ LONG ({len(long_list)} เหรียญ)</div>', unsafe_allow_html=True)

if long_list:
    for i in range(0, len(long_list), 3):
        cols = st.columns(3)
        for idx, coin in enumerate(long_list[i:i+3]):
            with cols[idx]:
                p_fmt = f"${coin['price']:,.4f}" if coin['price'] < 1.0 else f"${coin['price']:,.2f}"
                c_class = "price-change-pos" if coin['change'] >= 0 else "price-change-neg"
                c_sign = "+" if coin['change'] >= 0 else ""
                
                st.markdown(f"""
                <div class="coin-card">
                    <div class="card-header">
                        <div><span class="coin-name">{coin['symbol']}</span> <span class="cagr-badge">CAGR: +{coin['cagr']:.1f}%</span></div>
                        <span class="status-badge-long">LONG</span>
                    </div>
                    <div class="coin-full-name">{coin['name']}</div>
                    <div class="price-row">
                        <span class="current-price">{p_fmt}</span>
                        <span class="{c_class}">{c_sign}{coin['change']:.2f}%</span>
                        <span style="color:#595247; font-size:0.75rem;">ปิดล่าสุด</span>
                    </div>
                    <div>
                        <div class="rsi-val-long">{coin['rsi']:.1f}<span class="rsi-label">RSI 14 วัน</span></div>
                    </div>
                    <div class="progress-container">
                        <div class="progress-zone"></div>
                        <div class="progress-pointer-long" style="left: {coin['rsi']}%;"></div>
                    </div>
                    <div class="progress-labels">
                        <span>0</span><span>45</span><span>55</span><span>100</span>
                    </div>
                    <div class="history-box">
                        <p>🟢 <b>คงสถานะ LONG</b> — เหรียญเกรด A ผลตอบแทนอดีตเยี่ยม และโมเมนตัมปัจจุบันกำลังเลือกข้างขึ้นชัดเจน</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("ไม่มีเหรียญเกรดผ่านเกณฑ์ตัวไหนที่อยู่ในสถานะ LONG ณ วันนี้")


# --- 🔴 โซนเหรียญผ่านเกณฑ์แต่สถานะปัจจุบันให้ถือเงินสด CASH ---
st.markdown(f'<div class="section-title-cash">🔴 ผ่านเกณฑ์ CAGR > 20% แต่สถานะปัจจุบันให้ถือเงินสด ∙ CASH ({len(cash_list)} เหรียญ)</div>', unsafe_allow_html=True)

if cash_list:
    for i in range(0, len(cash_list), 3):
        cols = st.columns(3)
        for idx, coin in enumerate(cash_list[i:i+3]):
            with cols[idx]:
                p_fmt = f"${coin['price']:,.4f}" if coin['price'] < 1.0 else f"${coin['price']:,.2f}"
                c_class = "price-change-pos" if coin['change'] >= 0 else "price-change-neg"
                c_sign = "+" if coin['change'] >= 0 else ""
                
                st.markdown(f"""
                <div class="coin-card" style="opacity: 0.85; border: 1px solid #332a24;">
                    <div class="card-header">
                        <div><span class="coin-name" style="color:#d1cabc;">{coin['symbol']}</span> <span class="cagr-badge">CAGR: +{coin['cagr']:.1f}%</span></div>
                        <span class="status-badge-cash">CASH</span>
                    </div>
                    <div class="coin-full-name">{coin['name']}</div>
                    <div class="price-row">
                        <span class="current-price" style="color:#d1cabc;">{p_fmt}</span>
                        <span class="{c_class}">{c_sign}{coin['change']:.2f}%</span>
                        <span style="color:#595247; font-size:0.75rem;">ปิดล่าสุด</span>
                    </div>
                    <div>
                        <div class="rsi-val-cash">{coin['rsi']:.1f}<span class="rsi-label">RSI 14 วัน</span></div>
                    </div>
                    <div class="progress-container">
                        <div class="progress-zone"></div>
                        <div class="progress-pointer-cash" style="left: {coin['rsi']}%;"></div>
                    </div>
                    <div class="progress-labels">
                        <span>0</span><span>45</span><span>55</span><span>100</span>
                    </div>
                    <div class="history-box" style="background-color:#171212;">
                        <p style="color:#c48b8b;">⚠️ <b>ถือเงินสด (CASH)</b> — ในอดีตทำกำไรทบต้นได้ดีมาก แต่ ณ จังหวะปัจจุบันราคายังพักฐานหรือหลุดแนวรับเทรนไปแล้ว ให้ถือเงินสดรอรอบใหม่</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
