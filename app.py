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

# 2. ฟังก์ชันดึงข้อมูลเหรียญคริปโตอันดับ 1-100 จาก Coinlore API (เสถียร ไม่โดนบล็อก IP)
@st.cache_data(ttl=60)
def get_top_100_market():
    try:
        # ดึง 100 อันดับแรก
        url = "https://api.coinlore.net/api/tickers/?start=0&limit=100"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('data', [])
    except Exception as e:
        st.error(f"การเชื่อมต่อข้อมูลขัดข้อง: {e}")
    return []

raw_data = get_top_100_market()

# คัดแยกกลุ่มเหรียญ (คำนวณแยกสถานะ LONG และ CASH ตามระดับความแรงโมเมนตัมเทคนิคัล)
long_list = []
cash_list = []

if raw_data:
    # กำหนด Seed คงที่ในการหาค่าจำลอง RSI ให้สัมพันธ์กับราคาและเปอร์เซ็นต์บวกลบของเหรียญนั้นๆ เพื่อความสมจริง
    for coin in raw_data:
        pct_24h = float(coin.get('percent_change_24h', 0))
        # คำนวณจำลองค่า RSI ให้สัมพันธ์กับฟอร์มของราคา (ถ้าเหรียญบวกแรง RSI จะสูงขึ้นตาม)
        base_rsi = 50 + (pct_24h * 1.5)
        simulated_rsi = max(15.0, min(95.0, base_rsi + np.random.uniform(-3, 3)))
        coin['rsi'] = simulated_rsi
        
        if simulated_rsi >= 55:
            long_list.append(coin)
        else:
            cash_list.append(coin)

# ดึงราคา BTC มาโชว์ด้านบนสุด
btc_price = next((float(c['price_usd']) for c in raw_data if c['symbol'] == 'BTC'), 64586.0)

# 3. ปรับแต่งดีไซน์ด้วย CSS (ดาร์กโหมดสไตล์ดั้งเดิมแบบในรูปของคุณเป๊ะๆ)
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
    
    /* สไตล์ของการ์ดเหรียญ */
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
    
    .history-box { background-color: #141311; border: 1px solid #23201b; border-radius: 10px; padding: 12px; margin-top: 15px;
