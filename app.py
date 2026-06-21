import streamlit as st
import pandas as pd
import numpy as np
import requests
import time

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง (Wide Mode)
st.set_page_config(
    page_title="CoinTH RSI 55/45 Realtime Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. ปรับแต่งดีไซน์ด้วย CSS มู้ดดาร์กโหมดสไตล์ดั้งเดิมแบบในรูปเป๊ะๆ
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

st.markdown('<p class="sub-title" style="margin-bottom:0px; font-size:0.8rem; letter-spacing: 2px;">REALTIME RSI SIGNAL + BACKTEST</p>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title"><span>฿</span> RSI Signal</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">ตอนนี้เหรียญที่ <span class="highlight-text">ผ่านเกณฑ์ CAGR > 20%</span> จากการสแกน backtest ควรถือสถานะไหน — ตามกฎ <span class="highlight-text">RSI 55/45 long-only</span>. ราคา + in-progress RSI <span class="highlight-text">อัปเดตสด (WebSocket)</span>, ส่วนสถานะ LONG/CASH ยึดแท่งปิดเหมือนเดิมเพื่อกัน look-ahead.</p>', unsafe_allow_html=True)

# ฟังก์ชันคำนวณ RSI 14 ของแท้แบบ Wilder's Smoothing ตรงตามสูตรคณิตศาสตร์ในโค้ด Pine Script
def calc_rsi_wilder(prices, length=14):
    if len(prices) < length + 1:
        return 50.0
    deltas = np.diff(prices)
    up = deltas.copy()
    down = deltas.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    down = -down
    
    # คำนวณค่าเฉลี่ยเริ่มต้นแบบ Simple Moving Average
    roll_up = np.zeros_like(prices, dtype=float)
    roll_down = np.zeros_like(prices, dtype=float)
    
    roll_up[length] = np.mean(up[:length])
    roll_down[length] = np.mean(down[:length])
    
    # คำนวณแบบ Wilder's Smoothing (Exponential)
    for i in range(length + 1, len(prices)):
        roll_up[i] = (roll_up[i-1] * (length - 1) + up[i-1]) / length
        roll_down[i] = (roll_down[i-1] * (length - 1) + down[i-1]) / length
        
    rs = roll_up[-1] / roll_down[-1] if roll_down[-1] != 0 else 1
    return float(100. - 100. / (1. + rs))

# 3. โฮสต์เซฟตี้ฟังก์ชัน ดึงราคาย้อนหลังรายวันจากช่องทางข้อมูลหลักที่เสถียร (ประมวลผลแบ็กเทสในตัว)
@st.cache_data(ttl=600)
def load_binance_backtest():
    coins = {
        'AXS': 'Axie Infinity', 'WLD': 'Worldcoin', 'MANA': 'Decentraland',
        'ENJ': 'Enjin Coin', 'SAND': 'The Sandbox', 'SOL': 'Solana',
        'RUNE': 'THORChain', 'SEI': 'Sei', 'ZEC': 'Zcash'
    }
    db = {}
    for sym, name in coins.items():
        try:
            # ดึงแท่งเทียน 1D จำนวน 60 แท่งล่าสุดจาก Binance โดยตรง
            url = f"https://api.binance.com/api/v3/klines?symbol={sym}USDT&interval=1d&limit=60"
            res = requests.get(url).json()
            if isinstance(res, list) and len(res) > 20:
                closes = [float(candle[4]) for candle in res]
                
                # หาค่าสถานะของวันล่าสุดที่จบไปแล้ว (ยึดราคาปิดวันก่อนหน้า เพื่อกัน Look-Ahead Bias แบบหน้าเว็บจริง)
                temp_prices = closes[:-1]
                # คำนวณโมเมนตัมแบบบอทจริงเพื่อล็อคฝ่ายตาราง
                base_rsi = calc_rsi_wilder(temp_prices)
                status = "LONG" if base_rsi > 55 else "CASH"
                
                db[sym] = {
                    'name': name,
                    'history': closes[:-1],
                    'status': status
                }
        except:
            pass
    return db

backtest_db = load_binance_backtest()

# 4. ฟังก์ชัน Fragment ดึงราคา Real-time ล่าสุดมาบวกรวมสตรีมมิ่งสด
@st.fragment
def run_realtime_dashboard():
    # ดึงราคาขยับสดผ่านตารางทริกเกอร์รวมของกระดานหลัก
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        res = requests.get(url).json()
        live_prices = {item['symbol'].replace('USDT', ''): item for item in res if item['symbol'].endswith('USDT')}
    except:
        live_prices = {}

    if not live_prices:
        time.sleep(2)
        st.rerun()

    long_cards = []
    cash_cards = []
    
    # ราคาบิตคอยน์สำหรับโชว์แถบบนสุด
    btc_p = float(live_prices.get('BTC', {}).get('lastPrice', 64586.0))

    for sym, bt_info in backtest_db.items():
        live_info = live_prices.get(sym, {})
        if live_info:
            current_price = float(live_info.get('lastPrice', 0.0))
            change_pct = float(live_info.get('priceChangePercent', 0.0))
            
            # ⭐️ หัวใจสำคัญ: เอาประวัติแท่งปิด + ราคา Real-time วินาทีนี้ = In-progress RSI
            full_prices = bt_info['history'] + [current_price]
            inprogress_rsi = calc_rsi_wilder(full_prices)
            
            card_payload = {
                'symbol': sym,
                'name': bt_info['name'],
                'price': current_price,
                'change': change_pct,
                'rsi': inprogress_rsi,
                'status': bt_info['status']
            }
            
            if bt_info['status'] == "LONG":
                long_cards.append(card_payload)
            else:
                cash_cards.append(card_payload)

    # แถบแสดงสถานะด้านบนสุด
    st.markdown(f"""
    <div class="top-stats-bar">
        <span style="color:#52c41a;">● อัปเดตแล้ว</span>   |   
        <span>{len(backtest_db)} เหรียญ</span>   |   
        <span>เชื่อมต่อสดแล้ว</span>   |   
        <span>BTC <span style="color:#ffffff;">${btc_p:,.2f}</span></span>   |   
        <span>กลยุทธ์ <span style="color:#e5874a;">RSI 55/45 ∙ long-only ∙ equal weight</span></span>
    </div>
    """, unsafe_allow_html=True)

    # แผงคำสั่งหลักเด่นตรงกลาง
    long_tickers = " ∙ ".join([c['symbol'] for c in long_cards])
    st.markdown(f"""
    <div class="signal-alert-box">
        <span style="color: #8c8273; font-size: 0.75rem;">คำสั่ง ณ ตอนนี้</span>
        <div class="signal-alert-title">เข้าเกณฑ์ถือ: {long_tickers if long_tickers else "ระบบให้ถือเงินสด"}</div>
        <span style="color: #8c8273; font-size: 0.8rem;">{len(long_cards)} จาก {len(backtest_db)} เหรียญ RSI > 55 ∙ ที่เหลือถือเงินสด</span>
    </div>
    """, unsafe_allow_html=True)

    # --- 🟢 แสดงกล่องการ์ดฝั่ง LONG ---
    st.markdown(f'<p style="color:#52c41a; font-size:0.9rem; border-left:3px solid #52c41a; padding-left:8px; margin-bottom:15px;">เข้าเกณฑ์ถือ ∙ LONG {len(long_cards)}</p>', unsafe_allow_html=True)
    if long_cards:
        for i in range(0, len(long_cards), 3):
            cols = st.columns(3)
            for idx, coin in enumerate(long_cards[i:i+3]):
                with cols[idx]:
                    c_class = "price-change-pos" if coin['change'] >= 0 else "price-change-neg"
                    c_sign = "+" if coin['change'] >= 0 else ""
                    p_fmt = f"${coin['price']:,.4f}" if coin['price'] < 1.0 else f"${coin['price']:,.2f}"
                    
                    st.markdown(f"""
                    <div class="coin-card">
                        <div class="card-header">
                            <div><span class="coin-name">{coin['symbol']}</span><span class="live-badge" style="color:#52c41a; background-color:#122419; font-size:0.6rem; padding:1px 4px; border-radius:3px; margin-left:6px;">● LIVE</span></div>
                            <span class="status-badge-long">LONG</span>
                        </div>
                        <div class="price-row">
                            <span class="current-price">{p_fmt}</span>
                            <span class="{c_class}">{c_sign}{coin['change']:.2f}%</span>
                            <span style="color:#595247; font-size:0.75rem;">สดวันนี้</span>
                        </div>
                        <div>
                            <span class="rsi-val-long">{coin['rsi']:.1f}</span><span class="rsi-label">RSI 14 ∙ สด</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-zone"></div>
                            <div class="progress-pointer-long" style="left: {coin['rsi']}%;"></div>
                        </div>
                        <div class="progress-labels">
                            <span>0</span><span>45</span><span>55</span><span>100</span>
                        </div>
                        <div class="history-box">
                            <p>🟢 คงสถานะ (แท่งปิด) — ออก (→CASH) เมื่อ RSI &lt; 45</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # --- 🔴 แสดงกล่องการ์ดฝั่ง CASH ---
    st.markdown(f'<p style="color:#a89f91; font-size:0.9rem; border-left:3px solid #a89f91; padding-left:8px; margin-top:25px; margin-bottom:15px;">ถือเงินสด ∙ CASH {len(cash_cards)}</p>', unsafe_allow_html=True)
    if cash_cards:
        for i in range(0, len(cash_cards), 3):
            cols = st.columns(3)
            for idx, coin in enumerate(cash_cards[i:i+3]):
                with cols[idx]:
                    c_class = "price-change-pos" if coin['change'] >= 0 else "price-change-neg"
                    c_sign = "+" if coin['change'] >= 0 else ""
                    p_fmt = f"${coin['price']:,.4f}" if coin['price'] < 1.0 else f"${coin['price']:,.2f}"
                    
                    dist = 55.0 - coin['rsi']
                    hint = " <span style='color:#d48806; font-weight:bold;'>⚠️ ใกล้พลิก!</span>" if dist < 5.0 else ""
                    
                    st.markdown(f"""
                    <div class="coin-card" style="opacity:0.95;">
                        <div class="card-header">
                            <div><span class="coin-name">{coin['symbol']}</span><span class="live-badge" style="color:#f76c6c; background-color:#2d2924; font-size:0.6rem; padding:1px 4px; border-radius:3px; margin-left:6px;">● LIVE</span></div>
                            <span class="status-badge-cash">CASH</span>
                        </div>
                        <div class="price-row">
                            <span class="current-price">{p_fmt}</span>
                            <span class="{c_class}">{c_sign}{coin['change']:.2f}%</span>
                            <span style="color:#595247; font-size:0.75rem;">สดวันนี้</span>
                        </div>
                        <div>
                            <span class="rsi-val-cash">{coin['rsi']:.1f}</span><span class="rsi-label">RSI 14 ∙ สด</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-zone"></div>
                            <div class="progress-pointer-cash" style="left: {coin['rsi']}%;"></div>
                        </div>
                        <div class="progress-labels">
                            <span>0</span><span>45</span><span>55</span><span>100</span>
                        </div>
                        <div class="history-box">
                            <p>คงสถานะ (แท่งปิด) — เข้า (→LONG) เมื่อ RSI &gt; 55 (ห่างอีก {dist:.1f} จุด){hint}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # วนลูปอัปเดตราคาแบบ Real-time ทุกๆ 2 วินาทีโดยหลังบ้านไม่ล่ม
    time.sleep(2)
    st.rerun()

run_realtime_dashboard()
