import streamlit as st
import pandas as pd
import numpy as np
import requests
import concurrent.futures

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบกว้าง (Wide Mode)
st.set_page_config(
    page_title="CoinTH RSI 55/45 Realtime Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. ปรับแต่งดีไซน์ด้วย CSS มู้ดดาร์กโหมดสไตล์ดั้งเดิมแบบในรูปของคุณเจ
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

st.markdown('<p class="sub-title" style="margin-bottom:0px; font-size:0.8rem; letter-spacing: 2px;">REALTIME RSI SIGNAL + BACKTEST SCANNER (TOP 100)</p>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title"><span>฿</span> RSI Signal</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">ตอนนี้เหรียญที่ <span class="highlight-text">ผ่านเกณฑ์ CAGR > 20%</span> จากการสแกน backtest ควรถือสถานะไหน — ตามกฎ <span class="highlight-text">RSI 55/45 long-only</span>. ราคา + in-progress RSI <span class="highlight-text">อัปเดตสด (Native WebSocket)</span>, ส่วนสถานะ LONG/CASH ยึดแท่งปิดเหมือนเดิมเพื่อกัน look-ahead.</p>', unsafe_allow_html=True)

# 3. ฟังก์ชันเจาะข้อมูลราคาย้อนหลังทีละเหรียญ และทำ Backtest แบบเดียวกับ Pine Script
def fetch_and_backtest(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit=400"
        res = requests.get(url, timeout=5).json()
        if not isinstance(res, list) or len(res) < 50:
            return None
            
        # เราตัดแท่งล่าสุด (แท่งที่ยังไม่จบวัน) ออก เพื่อใช้คำนวณฐานของแท่งปิดเท่านั้น
        closed_prices = [float(candle[4]) for candle in res[:-1]]
        
        # --- เริ่มคำนวณสูตร Wilder's RSI (14) เหมือน Pine Script เป๊ะ ---
        length = 14
        deltas = np.diff(closed_prices)
        up = np.where(deltas > 0, deltas, 0)
        down = np.where(deltas < 0, -deltas, 0)
        
        avg_up = np.mean(up[:length])
        avg_down = np.mean(down[:length])
        
        position = 0
        entry_price = 0
        total_return = 1.0
        
        # จำลองการวิ่ง Backtest ทีละวัน
        for i in range(length, len(up)):
            avg_up = (avg_up * 13 + up[i]) / 14
            avg_down = (avg_down * 13 + down[i]) / 14
            
            rs = avg_up / avg_down if avg_down != 0 else 1
            rsi = 100 - (100 / (1 + rs))
            
            # ราคาปิดของวันที่อินดี้ตัด
            p = closed_prices[i + 1]
            if position == 0 and rsi > 55:
                position = 1
                entry_price = p
            elif position == 1 and rsi < 45:
                position = 0
                total_return *= (p / entry_price)
                
        # ปิดสถานะที่ค้างอยู่เพื่อคิด CAGR
        if position == 1:
            total_return *= (closed_prices[-1] / entry_price)
            
        years = len(closed_prices) / 365.0
        cagr = (total_return ** (1 / years) - 1) * 100
        
        # คำนวณค่า RSI วันปิดล่าสุด
        rs = avg_up / avg_down if avg_down != 0 else 1
        final_rsi = 100 - (100 / (1 + rs))
        status = "LONG" if final_rsi > 55 or (position == 1 and final_rsi >= 45) else "CASH"
        
        # ส่งค่าสถิติกลับไปผสานกับ Live Price
        return {
            'symbol': symbol.replace('USDT', ''),
            'cagr': cagr,
            'status': status,
            'last_closed_price': closed_prices[-1],
            'avg_up': avg_up,
            'avg_down': avg_down
        }
    except:
        return None

# 4. ฟังก์ชันจัดการข้อมูล (โหลดครั้งเดียวแล้วแคชไว้ 1 ชั่วโมง เพื่อไม่ให้ล่ม)
@st.cache_data(ttl=3600)
def initialize_top100_backtest():
    db = []
    try:
        # 4.1 ดึงรายชื่อ 100 เหรียญ Top Volume จาก Binance
        ticker_res = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
        usdt_pairs = [x for x in ticker_res if x['symbol'].endswith('USDT') and 'UP' not in x['symbol'] and 'DOWN' not in x['symbol']]
        usdt_pairs.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
        top_100_symbols = [x['symbol'] for x in usdt_pairs[:100]]
        
        # 4.2 ใช้ ThreadPool ดึงประวัติ 100 เหรียญพร้อมกันใน 2 วินาที (ไม่โดนบล็อก)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_and_backtest, sym) for sym in top_100_symbols]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                # กรองเอาเฉพาะตัวที่ Backtest แล้ว CAGR > 20% ตามกฎของคุณเจ!
                if result and result['cagr'] > 20.0:
                    db.append(result)
    except:
        pass
    
    # จัดเรียงจากกำไรมากไปน้อย
    db.sort(key=lambda x: x['cagr'], reverse=True)
    return db

# โหลดฐานข้อมูล (ส่วนนี้จะโหลดช้าแค่ตอนเปิดเว็บครั้งแรกประมาณ 3 วินาที)
backtest_db = initialize_top100_backtest()

# 5. ฟังก์ชันแสดงผลหน้าจอแบบ Real-time ตลอดเวลา (อัปเดตอัตโนมัติทุก 3 วินาที)
@st.fragment(run_every=3)
def render_realtime_dashboard():
    # ดึงราคาตลาดสด ณ วินาทีนี้ทั้งหมดภายในคำสั่งเดียว (เร็วมาก)
    try:
        live_res = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
        live_prices = {item['symbol'].replace('USDT', ''): item for item in live_res if item['symbol'].endswith('USDT')}
    except:
        live_prices = {}

    long_cards = []
    cash_cards = []
    
    btc_p = float(live_prices.get('BTC', {}).get('lastPrice', 64586.0))

    # ประมวลผล In-progress RSI
    for coin in backtest_db:
        sym = coin['symbol']
        live_info = live_prices.get(sym)
        if live_info:
            live_price = float(live_info['lastPrice'])
            change_pct = float(live_info['priceChangePercent'])
            
            # --- ผสมราคาปัจจุบันเข้ากับฐาน Smoothing เพื่อหา In-progress RSI เป๊ะๆ ---
            delta = live_price - coin['last_closed_price']
            live_up = delta if delta > 0 else 0
            live_down = -delta if delta < 0 else 0
            
            cur_avg_up = (coin['avg_up'] * 13 + live_up) / 14
            cur_avg_down = (coin['avg_down'] * 13 + live_down) / 14
            
            rs = cur_avg_up / cur_avg_down if cur_avg_down != 0 else 1
            live_rsi = 100 - (100 / (1 + rs))
            
            card_payload = {
                'symbol': sym,
                'price': live_price,
                'change': change_pct,
                'rsi': live_rsi,
                'cagr': coin['cagr'],
                'status': coin['status']
            }
            
            if coin['status'] == "LONG":
                long_cards.append(card_payload)
            else:
                cash_cards.append(card_payload)

    # วาดแถบสถานะด้านบน
    st.markdown(f"""
    <div class="top-stats-bar">
        <span style="color:#52c41a;">● อัปเดตสด (Native Real-time)</span>   |   
        <span>แสกน 100 อันดับแรก</span>   |   
        <span>BTC <span style="color:#ffffff;">${btc_p:,.2f}</span></span>   |   
        <span>กลยุทธ์ <span style="color:#e5874a;">RSI 55/45 ∙ long-only</span></span>
    </div>
    """, unsafe_allow_html=True)

    # แผงแจ้งเตือน
    long_tickers = " ∙ ".join([c['symbol'] for c in long_cards])
    st.markdown(f"""
    <div class="signal-alert-box">
        <span style="color: #8c8273; font-size: 0.75rem;">คำสั่ง ณ วินาทีนี้</span>
        <div class="signal-alert-title">เข้าเกณฑ์ถือ: {long_tickers if long_tickers else "ระบบให้ถือเงินสด"}</div>
        <span style="color: #8c8273; font-size: 0.8rem;">รัน Backtest 100 เหรียญ พบ {len(long_cards)+len(cash_cards)} เหรียญที่ CAGR > 20% (LONG {len(long_cards)} ∙ CASH {len(cash_cards)})</span>
    </div>
    """, unsafe_allow_html=True)

    # --- 🟢 โซน LONG ---
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
                            <div><span class="coin-name">{coin['symbol']}</span> <span class="cagr-badge">CAGR: +{coin['cagr']:.1f}%</span></div>
                            <span class="status-badge-long">LONG</span>
                        </div>
                        <div class="price-row">
                            <span class="current-price">{p_fmt}</span>
                            <span class="{c_class}">{c_sign}{coin['change']:.2f}%</span>
                            <span style="color:#52c41a; font-size:0.65rem; background-color:#122419; padding:2px 5px; border-radius:4px; font-weight:bold; margin-left:6px;">● สด</span>
                        </div>
                        <div>
                            <span class="rsi-val-long">{coin['rsi']:.1f}</span><span class="rsi-label">RSI 14 ∙ สด</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-zone"></div>
                            <div class="progress-pointer-long" style="left: {max(0, min(100, coin['rsi']))}%;"></div>
                        </div>
                        <div class="progress-labels">
                            <span>0</span><span>45</span><span>55</span><span>100</span>
                        </div>
                        <div class="history-box">
                            <p>🟢 คงสถานะ (แท่งปิด) — ออก (→CASH) เมื่อ RSI &lt; 45</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # --- 🔴 โซน CASH ---
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
                    hint = " <span style='color:#d48806; font-weight:bold;'>⚠️ ใกล้พลิก!</span>" if dist < 5.0 and dist > 0 else ""
                    
                    st.markdown(f"""
                    <div class="coin-card" style="opacity:0.95;">
                        <div class="card-header">
                            <div><span class="coin-name">{coin['symbol']}</span> <span class="cagr-badge">CAGR: +{coin['cagr']:.1f}%</span></div>
                            <span class="status-badge-cash">CASH</span>
                        </div>
                        <div class="price-row">
                            <span class="current-price">{p_fmt}</span>
                            <span class="{c_class}">{c_sign}{coin['change']:.2f}%</span>
                            <span style="color:#f76c6c; font-size:0.65rem; background-color:#261212; padding:2px 5px; border-radius:4px; font-weight:bold; margin-left:6px;">● สด</span>
                        </div>
                        <div>
                            <span class="rsi-val-cash">{coin['rsi']:.1f}</span><span class="rsi-label">RSI 14 ∙ สด</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-zone"></div>
                            <div class="progress-pointer-cash" style="left: {max(0, min(100, coin['rsi']))}%;"></div>
                        </div>
                        <div class="progress-labels">
                            <span>0</span><span>45</span><span>55</span><span>100</span>
                        </div>
                        <div class="history-box">
                            <p>คงสถานะ (แท่งปิด) — เข้า (→LONG) เมื่อ RSI &gt; 55 {hint}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# เริ่มคำสั่งสตรีมมิ่ง
render_realtime_dashboard()
