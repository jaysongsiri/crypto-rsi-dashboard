import streamlit as st
import pandas as pd
import numpy as np
import requests
import time

# 1. ตั้งค่าหน้าเว็บกว้าง (Wide Mode)
st.set_page_config(
    page_title="CoinTH RSI 55/45 Realtime Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. ปรับแต่งสไตล์ดีไซน์ดาร์กโหมดตามมู้ดรูปแรกของคุณ
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

# 3. ส่วนหัวข้อเว็บบอร์ด (Static Header)
st.markdown('<p class="sub-title" style="margin-bottom:0px; font-size:0.8rem; letter-spacing: 2px;">REALTIME RSI SIGNAL + BACKTEST SCANNER</p>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title"><span>฿</span> RSI Signal</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">ตอนนี้เหรียญที่ <span class="highlight-text">ผ่านเกณฑ์ CAGR > 20%</span> จากการสแกน backtest ควรถือสถานะไหน — ตามกฎ <span class="highlight-text">RSI 55/45 long-only</span>. ราคา + in-progress RSI <span class="highlight-text">อัปเดตสด</span>, ส่วนสถานะ LONG/CASH ยึดแท่งปิดเหมือนเดิมเพื่อกัน look-ahead.</p>', unsafe_allow_html=True)

# ฟังก์ชันคำนวณ RSI 14 จากลิสต์ราคาปิด
def calc_rsi_list(prices, length=14):
    if len(prices) < length + 1:
        return [50.0] * len(prices)
    deltas = np.diff(prices)
    seed = deltas[:length]
    up = seed[seed >= 0].sum() / length
    down = -seed[seed < 0].sum() / length
    rs = up / down if down != 0 else 1
    rsi = np.zeros_like(prices)
    rsi[:length] = 100. - 100. / (1. + rs)
    
    for i in range(length, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up * (length - 1) + upval) / length
        down = (down * (length - 1) + downval) / length
        rs = up / down if down != 0 else 1
        rsi[i] = 100. - 100. / (1. + rs)
    return rsi.tolist()

# ฟังก์ชันดึงประวัติราคาและทำ Backtest เพื่อหาผลประโยชน์ล่วงหน้าและ CAGR ย้อนหลัง 2 ปี
@st.cache_data(ttl=1800)  # ดึงชุดประวัติศาสตร์แคชไว้ 30 นาที
def load_backtest_data():
    coins_info = {
        'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'SOL': 'Solana', 'BNB': 'BNB', 
        'AXS': 'Axie Infinity', 'WLD': 'Worldcoin', 'MANA': 'Decentraland', 
        'ADA': 'Cardano', 'AVAX': 'Avalanche', 'LINK': 'Chainlink', 'NEAR': 'NEAR Protocol'
    }
    
    results = {}
    for sym, name in coins_info.items():
        try:
            url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={sym}&tsym=USD&limit=730"
            res = requests.get(url).json()
            data_list = res.get('Data', {}).get('Data', [])
            
            if len(data_list) > 100:
                df = pd.DataFrame(data_list)
                prices = df['close'].tolist()
                rsi_vals = calc_rsi_list(prices)
                
                # จำลองการเทรดแบบปิดแท่งจริงเพื่อหาผลรวมย้อนหลัง
                position = 0
                total_return = 1.0
                entry_p = 0
                
                # วนลูปเช็กแท่งปิดจนถึงวันก่อนหน้า (กัน Look-Ahead)
                for i in range(len(prices) - 1):
                    rsi_v = rsi_vals[i]
                    p = prices[i]
                    if position == 0 and rsi_v > 55:
                        position = 1
                        entry_p = p
                    elif position == 1 and rsi_v < 45:
                        position = 0
                        total_return *= (p / entry_p)
                
                # สรุปผลสถานะแท่งปิดล่าสุด (ข้อมูลวันก่อนหน้าจริง ๆ)
                last_closed_rsi = rsi_vals[-2]
                last_closed_position = 1 if last_closed_rsi > 55 or (position == 1 and last_closed_rsi >= 45) else 0
                confirmed_status = "LONG" if last_closed_position == 1 else "CASH"
                
                # คำนวณ CAGR ทบต้นต่อปี
                cagr = (total_return ** (1.0 / 2.0) - 1.0) * 100
                
                # เราจะเซฟชุดตัวเลขในอดีตและฐานคำนวณเอาไว้สตรีมสดต่อ
                results[sym] = {
                    'name': name,
                    'history_prices': prices[:-1], # เก็บเฉพาะแท่งปิดในอดีต
                    'cagr': cagr,
                    'confirmed_status': confirmed_status
                }
        except:
            pass
    return results

backtest_db = load_backtest_data()

# 4. ส่วน Fragment ข้อมูลเรียลไทม์ (ราคาและค่า RSI ในแท่งปัจจุบันจะอัปเดตแบบสดๆ ทุกๆ 3 วินาที)
@st.fragment
def run_realtime_stream():
    # ดึงราคาปัจจุบัน ณ วินาทีนี้จากหน้าบ้านสตรีมมิ่งมาประกบ
    try:
        url = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC,ETH,SOL,BNB,AXS,WLD,MANA,ADA,AVAX,LINK,NEAR&tsyms=USD"
        live_res = requests.get(url).json().get('RAW', {})
    except:
        live_res = {}
        
    # ดักกรองเคสถ้า API เกิดขัดข้องชั่วขณะ
    if not live_res:
        time.sleep(3)
        st.rerun()
        
    # ประมวลผลเหรียญที่เข้าเกณฑ์ CAGR > 20%
    long_cards = []
    cash_cards = []
    
    for sym, bt_info in backtest_db.items():
        # เช็กเงื่อนไขกลั่นกรองขั้นแรก: ต้องผ่านเกณฑ์ CAGR > 20% เท่านั้น!
        if bt_info['cagr'] > 20.0:
            coin_live = live_res.get(sym, {}).get('USD', {})
            if coin_live:
                live_price = coin_live.get('PRICE', 0.0)
                change_24h = coin_live.get('CHANGEPCT24HOUR', 0.0)
                
                # คำนวณ In-progress RSI: เอาประวัติแท่งปิดในอดีตมาบวกราคา ณ วินาทีนี้เข้าไปในแท่งล่าสุด
                temp_prices = bt_info['history_prices'] + [live_price]
                updated_rsi_list = calc_rsi_list(temp_prices)
                inprogress_rsi = updated_rsi_list[-1]  # ดึงค่า RSI ล่าสุดของวินาทีนี้
                
                card_data = {
                    'symbol': sym,
                    'name': bt_info['name'],
                    'price': live_price,
                    'change': change_24h,
                    'rsi': inprogress_rsi,
                    'cagr': bt_info['cagr'],
                    'confirmed_status': bt_info['confirmed_status']
                }
                
                # แยกจัดหมวดหมู่การ์ดตามสถานะแท่งปิด (LONG/CASH ยึดแท่งปิดเหมือนเดิมเพื่อกัน look-ahead)
                if bt_info['confirmed_status'] == "LONG":
                    long_cards.append(card_data)
                else:
                    cash_cards.append(card_data)
                    
    # ดึงราคา BTC โชว์แถบบน
    btc_p = live_res.get('BTC', {}).get('USD', {}).get('PRICE', 64586.0)
    
    st.markdown(f"""
    <div class="top-stats-bar">
        <span style="color:#52c41a;">● สัญญาณ WebSocket สด (ราคา + RSI อัปเดตแบบเรียลไทม์)</span>   |   
        <span>BTC ล่าสุด: <span style="color:#ffffff;">${btc_p:,.2f}</span></span>   |   
        <span>กลยุทธ์ <span style="color:#e5874a;">RSI 55/45 ∙ long-only</span></span>   |   
        <span>สถานะ LONG/CASH ยึดตามราคาแท่งปิดจริงอย่างเข้มงวด</span>
    </div>
    """, unsafe_allow_html=True)
    
    # สรุปภาพรวมคำสั่งพอร์ต
    long_tickers = " ∙ ".join([c['symbol'] for c in long_cards])
    st.markdown(f"""
    <div class="signal-alert-box">
        <span style="color: #8c8273; font-size: 0.75rem;">คำสั่งบอท ณ วินาทีนี้</span>
        <div class="signal-alert-title">เข้าเกณฑ์ถือครอง (LONG): {long_tickers if long_tickers else "ถือเงินสดทั้งหมด"}</div>
        <span style="color: #8c8273; font-size: 0.8rem;">กรองเฉพาะเหรียญเกรดดีเยี่ยม CAGR > 20% สัญญาส่งตรงแบบไร้ Look-Ahead Bias</span>
    </div>
    """, unsafe_allow_html=True)
    
    # --- แสดงโซนการ์ดฝั่ง LONG ---
    st.markdown(f'<div class="section-title-long">🟢 ผ่านเกณฑ์ CAGR > 20% ∙ คงสถานะซื้อถือครอง LONG ({len(long_cards)} เหรียญ)</div>', unsafe_allow_html=True)
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
                        <div class="coin-full-name">{coin['name']}</div>
                        <div class="price-row">
                            <span class="current-price">{p_fmt}</span>
                            <span class="{c_class}">{c_sign}{coin['change']:.2f}%</span>
                            <span style="color:#52c41a; font-size:0.65rem; background-color:#122419; padding:2px 5px; border-radius:4px; font-weight:bold;">● สด</span>
                        </div>
                        <div>
                            <div class="rsi-val-long">{coin['rsi']:.1f}<span class="rsi-label">RSI 14 (แท่งปัจจุบัน)</span></div>
                        </div>
                        <div class="progress-container">
                            <div class="progress-zone"></div>
                            <div class="progress-pointer-long" style="left: {coin['rsi']}%;"></div>
                        </div>
                        <div class="progress-labels">
                            <span>0</span><span>45</span><span>55</span><span>100</span>
                        </div>
                        <div class="history-box">
                            <p>🟢 <b>สถานะยึดแท่งปิด</b> — แท่งปัจจุบัน RSI วิ่งอยู่ที่ระดับ {coin['rsi']:.1f} (ออกเมื่อแท่งปิดจริงหลุด 45)</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("ไม่มีเหรียญที่ผ่านเกณฑ์ตัวไหนอยู่ในสถานะ LONG ณ ขณะนี้")
        
    # --- แสดงโซนการ์ดฝั่ง CASH ---
    st.markdown(f'<div class="section-title-cash">🔴 ผ่านเกณฑ์ CAGR > 20% ∙ คงสถานะถือเงินสดรักษาต้นทุน CASH ({len(cash_cards)} เหรียญ)</div>', unsafe_allow_html=True)
    if cash_cards:
        for i in range(0, len(cash_cards), 3):
            cols = st.columns(3)
            for idx, coin in enumerate(cash_cards[i:i+3]):
                with cols[idx]:
                    c_class = "price-change-pos" if coin['change'] >= 0 else "price-change-neg"
                    c_sign = "+" if coin['change'] >= 0 else ""
                    p_fmt = f"${coin['price']:,.4f}" if coin['price'] < 1.0 else f"${coin['price']:,.2f}"
                    
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
                            <span style="color:#f76c6c; font-size:0.65rem; background-color:#261212; padding:2px 5px; border-radius:4px; font-weight:bold;">● สด</span>
                        </div>
                        <div>
                            <div class="rsi-val-cash">{coin['rsi']:.1f}<span class="rsi-label">RSI 14 (แท่งปัจจุบัน)</span></div>
                        </div>
                        <div class="progress-container">
                            <div class="progress-zone"></div>
                            <div class="progress-pointer-cash" style="left: {coin['rsi']}%;"></div>
                        </div>
                        <div class="progress-labels">
                            <span>0</span><span>45</span><span>55</span><span>100</span>
                        </div>
                        <div class="history-box" style="background-color:#171212;">
                            <p style="color:#c48b8b;">⚠️ <b>สถานะยึดแท่งปิด</b> — ถือเงินสดปลอดภัย แท่งปัจจุบันกำลังขยับทำฐานสัญญาณใหม่</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
    # หน่วงเวลา 3 วินาทีแล้วสั่งให้โหลดค่าเรียลไทม์แท่งปัจจุบันรอบใหม่
    time.sleep(3)
    st.rerun()

# เปิดรันระบบเรียลไทม์สตรีมมิ่ง
run_realtime_stream()
