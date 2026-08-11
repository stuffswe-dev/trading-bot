import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import io
import matplotlib.pyplot as plt
import plotly.graph_objects as pd_go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pro Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme polish
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2a2e39;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR & SETTINGS ---
st.sidebar.title("⚙️ Inställningar")
telegram_token = st.sidebar.text_input("Telegram Bot Token", type="password")
telegram_chat_id = st.sidebar.text_input("Telegram Chat ID")

market_choice = st.sidebar.radio(
    "Välj Marknad", 
    ["Sverige (Large Cap)", "Sverige (Mid Cap)", "USA (US Tech & Megacaps)"]
)

# NYTT: Väljare för Tidsram
timeframe_choice = st.sidebar.selectbox(
    "⏱️ Välj Tidsram (Timeframe)",
    ["15 Minuter (15m)", "1 Timme (1h)", "4 Timmar (4h)", "Dagsgraf (1d)"],
    index=0
)

# Mappning till yfinance-intervall och historik-period
tf_map = {
    "15 Minuter (15m)": {"interval": "15m", "period": "5d"},
    "1 Timme (1h)":     {"interval": "1h",  "period": "1mo"},
    "4 Timmar (4h)":    {"interval": "1h",  "period": "3mo"}, # yfinance saknar ren 4h, simuleras via 1h/resample
    "Dagsgraf (1d)":    {"interval": "1d",  "period": "6mo"}
}

chosen_tf = tf_map[timeframe_choice]

st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Automatisk Bevakning")
auto_scan = st.sidebar.toggle("Aktivera Auto-skanning", value=True)
refresh_interval_min = st.sidebar.slider("Intervall (minuter)", min_value=1, max_value=30, value=15, step=1)

if auto_scan:
    count = st_autorefresh(interval=refresh_interval_min * 60 * 1000, key="trading_bot_refresh")
    st.sidebar.caption(f"🟢 Auto-skanning aktiv (Körs var {refresh_interval_min}:e min)")

st.sidebar.markdown("---")
# Test-knapp för Telegram
if st.sidebar.button("🧪 Skicka Test-Telegram"):
    if telegram_token and telegram_chat_id:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {"chat_id": telegram_chat_id, "text": "✅ *Testnotis från din Tradingbot!* Systemet fungerar utmärkt.", "parse_mode": "Markdown"}
        try:
            r = requests.post(url, json=payload)
            if r.status_code == 200: st.sidebar.success("Testnotis skickad!")
            else: st.sidebar.error("Kunde inte skicka (fel Token/Chat ID).")
        except Exception as e: st.sidebar.error(f"Fel: {e}")
    else:
        st.sidebar.warning("Fyll i Token och Chat ID först!")

# --- BEVAKNINGSLISTOR ---
WATCHLIST_LARGE_CAP = [
    "ABB.ST", "ALFA.ST", "ALIV-SDB.ST", "ASSA-B.ST", "AZN.ST", "ATCO-A.ST", "ATCO-B.ST",
    "AURA.ST", "BALD-B.ST", "BEIJ-B.ST", "BOL.ST", "BONAV-B.ST", "CAST.ST", "EPI-A.ST",
    "EPI-B.ST", "ERIC-A.ST", "ERIC-B.ST", "ESSITY-A.ST", "ESSITY-B.ST", "EVO.ST", "FABG.ST",
    "GETI-B.ST", "HEXA-B.ST", "HM-B.ST", "HOLM-B.ST", "HPOL-B.ST", "INVE-A.ST", "INVE-B.ST",
    "INDT.ST", "INDU-A.ST", "INDU-C.ST", "JM.ST", "KINV-B.ST", "LIFCO-B.ST", "LUND-B.ST",
    "NCAB.ST", "NIBE-B.ST", "NOBI.ST", "NOM.ST", "NYF.ST", "SCA-A.ST", "SCA-B.ST", "SEB-A.ST",
    "SEB-C.ST", "SECT-B.ST", "SHB-A.ST", "SHB-B.ST", "SINCH.ST", "SKF-A.ST", "SKF-B.ST",
    "SWED-A.ST", "SWMA.ST", "TEL2-A.ST", "TEL2-B.ST", "TELIA.ST", "THULE.ST", "TIGO-SDB.ST",
    "TREL-B.ST", "VOLV-A.ST", "VOLV-B.ST", "WALL-B.ST", "WIHL.ST", "SAAB-B.ST", "SSAB-A.ST",
    "SSAB-B.ST", "LUN.ST"
]

WATCHLIST_MID_CAP = [
    "ACAD.ST", "AFRY.ST", "ALLEI.ST", "ANOD-B.ST", "ARJO-B.ST", "ARNW.ST", "ATT.ST",
    "BAKKA.ST", "BEGR.ST", "BILI-A.ST", "BIOG-B.ST", "BIOA-B.ST", "BONEX.ST", "BOOZT.ST",
    "BULT.ST", "BURE.ST", "CAT-B.ST", "CATE.ST", "CEVI.ST", "CLAS-B.ST", "CRED-A.ST",
    "CTM.ST", "DIOS.ST", "DOM.ST", "DUST.ST", "EAST.ST", "EPRO-B.ST", "FAG.ST", "FING-B.ST",
    "GPG.ST", "HEBA-B.ST", "HEM.ST", "HMS.ST", "HOFI.ST", "HUMAN.ST", "INSTAL.ST", "INWI.ST",
    "ITAB-B.ST", "K2A-B.ST", "KAR.ST", "KIND-SDB.ST", "KNOW.ST", "LAGR-B.ST", "LIND-B.ST",
    "LOOMIS.ST", "MEKO.ST", "MIPS.ST", "MTRS.ST", "MYCR.ST", "NEOB.ST", "NOLA-B.ST",
    "NP3.ST", "OEM-B.ST", "PNDX-B.ST", "RATO-B.ST", "RESURS.ST", "RISO-B.ST", "SAS.ST",
    "SCST.ST", "SDIP-B.ST", "SINT.ST", "STILL.ST", "SVOLDER-B.ST", "TROAX.ST", "VBG-B.ST",
    "VITR.ST", "VOLO.ST", "WALL-B.ST", "XANO-B.ST"
]

WATCHLIST_US = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AMD", 
    "AVGO", "QCOM", "TXN", "MU", "INTC", "AMAT", "LRCX", "ADI",
    "PLTR", "CRM", "NOW", "PANW", "SNOW", "SHOP", "NET", "COIN", "UBER", "ABNB",
    "COST", "NFLX", "DIS", "BA", "CAT", "JPM", "GS", "V", "MA"
]

if market_choice == "Sverige (Large Cap)":
    watchlist = WATCHLIST_LARGE_CAP
    currency_symbol = "SEK"
elif market_choice == "Sverige (Mid Cap)":
    watchlist = WATCHLIST_MID_CAP
    currency_symbol = "SEK"
else:
    watchlist = WATCHLIST_US
    currency_symbol = "$"

# --- VWAP CALCULATOR ---
def calculate_vwap(df):
    df = df.copy()
    df['Date'] = df.index.date
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['TPV'] = df['TP'] * df['Volume']
    df['Cum_Volume'] = df.groupby('Date')['Volume'].cumsum()
    df['Cum_TPV'] = df.groupby('Date')['TPV'].cumsum()
    df['VWAP'] = df['Cum_TPV'] / df['Cum_Volume']
    return df

# --- INDICATOR CALCULATIONS ---
def calculate_indicators(df):
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # ATR
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df['ATR'] = true_range.rolling(14).mean()

    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    # Candlestick metrics
    df['Body'] = (df['Close'] - df['Open']).abs()
    df['Lower_Shadow'] = np.where(df['Close'] >= df['Open'], df['Open'] - df['Low'], df['Close'] - df['Low'])

    # VWAP
    df = calculate_vwap(df)

    return df

# --- GENERATE TELEGRAM CHART IMAGE ---
def generate_telegram_chart(df, ticker, pattern, entry, stop_loss, take_profit, tf_label):
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    
    recent_df = df.tail(40)
    
    ax1.plot(recent_df.index, recent_df['Close'], label='Pris', color='#ffffff', linewidth=1.5)
    ax1.plot(recent_df.index, recent_df['EMA20'], label='EMA 20', color='#2962ff', alpha=0.7)
    ax1.plot(recent_df.index, recent_df['VWAP'], label='VWAP (Stöd)', color='#ffd600', linewidth=1.8, linestyle=':')

    ax1.axhline(entry, color='#00e676', linestyle='-', linewidth=1.2, label=f'Entry ({entry})')
    ax1.axhline(take_profit, color='#29b6f6', linestyle='--', linewidth=1.2, label=f'Take Profit ({take_profit})')
    ax1.axhline(stop_loss, color='#ff5252', linestyle='--', linewidth=1.2, label=f'Stop Loss ATR ({stop_loss})')

    ax1.set_title(f"🚀 {ticker.replace('.ST','')} - {pattern} ({tf_label})", fontsize=14, color='#00e676', fontweight='bold')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(True, color='#2a2e39', alpha=0.5)

    colors = ['#00e676' if val >= 0 else '#ff5252' for val in recent_df['MACD_Hist']]
    ax2.bar(recent_df.index, recent_df['MACD_Hist'], color=colors, alpha=0.6)
    ax2.set_title("MACD Momentum", fontsize=9, color='#aaaaaa')
    ax2.grid(True, color='#2a2e39', alpha=0.5)

    plt.xticks(rotation=30)
    plt.tight_layout()

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=150)
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

# --- SEND TELEGRAM PHOTO ---
def send_telegram_photo(token, chat_id, caption, image_buf):
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    files = {'photo': ('chart.png', image_buf, 'image/png')}
    data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=data, files=files)
    except Exception as e:
        st.error(f"Telegram-fel: {e}")

# --- SCANNING LOGIC ---
def scan_stock(ticker, interval, period):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty or len(df) < 40:
            return None, None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = calculate_indicators(df)

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        latest_time = df.index[-1].strftime('%Y-%m-%d %H:%M')

        # Mönster
        is_hammer = (latest['Lower_Shadow'] >= 1.3 * latest['Body']) and (latest['Body'] > 0)
        is_engulfing = (prev['Close'] < prev['Open']) and (latest['Close'] > latest['Open']) and (latest['Close'] >= prev['Open'])

        # ELIT-FILTER (EMA + RSI + MACD + VWAP)
        uptrend = latest['EMA20'] > latest['EMA50']
        rsi_ok = latest['RSI'] < 58
        macd_turning = latest['MACD_Hist'] > prev['MACD_Hist']
        
        above_vwap = latest['Close'] > latest['VWAP']
        near_vwap_support = latest['Low'] <= latest['VWAP'] * 1.01

        pattern = None
        if is_engulfing: pattern = "Bullish Engulfing 🟢"
        elif is_hammer: pattern = "Hammer 🔨"

        if pattern and uptrend and rsi_ok and macd_turning and above_vwap and near_vwap_support:
            entry = round(float(latest['Close']), 2)
            atr_val = float(latest['ATR'])
            
            stop_loss = round(entry - (atr_val * 1.2), 2)
            risk = entry - stop_loss
            if risk <= 0: return None, df
            take_profit = round(entry + (risk * 1.5), 2)

            diff_tp = round(take_profit - entry, 2)
            pct_tp = round(((take_profit - entry) / entry) * 100, 2)

            description = (
                f"Sannolikheten för uppgång är hög på **{timeframe_choice}**. "
                f"Förväntad vinstpotential är **+{pct_tp}% ({diff_tp} {currency_symbol})**. "
                f"Priset handlas över VWAP ({round(latest['VWAP'],2)}) och stöder vid mönstret **{pattern}**."
            )

            return {
                'Ticker': ticker.replace('.ST',''),
                'Full_Ticker': ticker,
                'Tid': latest_time,
                'Mönster': pattern,
                'Pris': entry,
                'Stop Loss': stop_loss,
                'Take Profit': take_profit,
                'RSI': round(float(latest['RSI']), 1),
                'VWAP': round(float(latest['VWAP']), 2),
                'Pct_TP': pct_tp,
                'Beskrivning': description
            }, df

        return None, df

    except Exception:
        return None, None

# --- DASHBOARD UI ---
st.title("⚡ Pro Trading Live Dashboard")
now_time = datetime.now().strftime('%H:%M:%S')
st.caption(f"Flexibel Multidsram-skanning | Senaste skanning: **{now_time}**")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Vald Marknad", market_choice)
with col2:
    st.metric("Vald Tidsram", timeframe_choice)
with col3:
    st.metric("Antal Aktier i Listan", len(watchlist))
with col4:
    status_label = f"Auto-skanning ({refresh_interval_min}m)" if auto_scan else "Manuell"
    st.metric("Skanningsläge", status_label)

st.markdown("---")

# Kör skanning
with st.spinner(f"Skannar {len(watchlist)} aktier i {market_choice} på {timeframe_choice}..."):
    signals_found = []
    
    for ticker in watchlist:
        signal, df = scan_stock(ticker, chosen_tf["interval"], chosen_tf["period"])
        if signal:
            signals_found.append((signal, df))

    if signals_found:
        st.success(f"🔥 [{now_time}] Hittade {len(signals_found)} KÖPSIGNALER på {timeframe_choice}!")
        
        for sig, df in signals_found:
            with st.expander(f"📌 {sig['Ticker']} - {sig['Mönster']} (Vinstpotential: +{sig['Pct_TP']}%)", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Entry (Pris)", f"{sig['Pris']} {currency_symbol}")
                c2.metric("Stop Loss (ATR)", f"{sig['Stop Loss']} {currency_symbol}", delta=f"{round(sig['Stop Loss']-sig['Pris'],2)}")
                c3.metric("Take Profit", f"{sig['Take Profit']} {currency_symbol}", delta=f"+{sig['Pct_TP']}%")
                c4.metric("VWAP Stöd", f"{sig['VWAP']} {currency_symbol}")

                st.markdown(f"**💡 Motivering:** {sig['Beskrivning']}")

                # Plotly Candlestick-graf med VWAP
                fig_plotly = pd_go.Figure()
                fig_plotly.add_trace(pd_go.Candlestick(
                    x=df.index[-30:],
                    open=df['Open'][-30:],
                    high=df['High'][-30:],
                    low=df['Low'][-30:],
                    close=df['Close'][-30:],
                    name="Pris"
                ))
                fig_plotly.add_trace(pd_go.Scatter(
                    x=df.index[-30:],
                    y=df['VWAP'][-30:],
                    mode='lines',
                    name='VWAP (Stöd)',
                    line=dict(color='#ffd600', width=2)
                ))
                fig_plotly.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_plotly, use_container_width=True)

                # Telegram Notis
                if telegram_token and telegram_chat_id:
                    img_buf = generate_telegram_chart(df, sig['Ticker'], sig['Mönster'], sig['Pris'], sig['Stop Loss'], sig['Take Profit'], timeframe_choice)
                    caption = (
                        f"🔥 *KÖPSIGNAL ({timeframe_choice}): {sig['Ticker']}*\n\n"
                        f"📌 *Mönster:* `{sig['Mönster']}`\n"
                        f"• *Entry:* `{sig['Pris']} {currency_symbol}`\n"
                        f"• *Take Profit:* `{sig['Take Profit']} {currency_symbol}` (*+{sig['Pct_TP']}%*)\n"
                        f"• *Stop Loss (ATR):* `{sig['Stop Loss']} {currency_symbol}`\n"
                        f"• *VWAP Stöd:* `{sig['VWAP']} {currency_symbol}`\n\n"
                        f"💡 *Motivering:*\n{sig['Beskrivning']}"
                    )
                    send_telegram_photo(telegram_token, telegram_chat_id, caption, img_buf)
                    st.info("✅ Grafbild och köpsignal skickad till Telegram!")

    else:
        st.info(f"ℹ️ [{now_time}] Inga aktier i {market_choice} ger signal på **{timeframe_choice}** just nu.")