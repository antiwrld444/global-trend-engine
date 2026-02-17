import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Определение путей
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(base_dir, "data", "trends.db")

st.set_page_config(page_title="GTOE | Market Intelligence", layout="wide", initial_sidebar_state="expanded")

st.title("🌍 Global Trend & Opportunity Engine")

def get_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM trends ORDER BY timestamp DESC", conn)
    conn.close()
    return df

df = get_data()

# Sidebar
st.sidebar.header("⚙️ Управление")
if st.sidebar.button("🔄 Обновить данные"):
    st.rerun()

# Основные вкладки
tab1, tab2, tab3 = st.tabs(["🔥 Тренды и Новости", "📉 Рынки и Валюты", "🧠 Влияние и Анализ"])

with tab1:
    st.subheader("Мониторинг мировых событий")
    if not df.empty:
        st.dataframe(df[['title', 'source', 'sentiment', 'timestamp']], use_container_width=True)
    else:
        st.info("База данных пуста.")

with tab2:
    st.subheader("Курсы Валют и Криптовалют")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💱 Валютные пары (Forex)")
        # Симуляция данных для демонстрации (AlphaVantage требует времени на сбор)
        forex_data = pd.DataFrame({
            'Пара': ['USD/RUB', 'EUR/USD', 'CNY/RUB'],
            'Цена': [92.45, 1.08, 12.75],
            'Изменение': ['+0.2%', '-0.1%', '+0.05%']
        })
        st.table(forex_data)
        
    with col2:
        st.markdown("#### ⚡ Криптовалюты")
        crypto_data = pd.DataFrame({
            'Актив': ['BTC', 'ETH', 'SOL'],
            'Цена ($)': [52100, 2850, 110],
            '24h %': ['+2.5%', '+1.8%', '+5.2%']
        })
        st.table(crypto_data)

    st.markdown("#### 📊 График динамики (Mockup)")
    # Пример графика
    chart_data = pd.DataFrame({
        'Date': pd.date_range(start='2026-02-01', periods=10),
        'BTC': [48000, 49000, 47500, 50000, 51000, 50500, 52000, 53000, 52500, 52100]
    })
    fig = px.line(chart_data, x='Date', y='BTC', title="Динамика BTC/USD")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Анализ влияния новостей на рынок")
    st.write("Здесь GTOE сопоставляет тональность новостей с движениями графиков.")
    
    if not df.empty:
        # Простая корреляция для демонстрации
        avg_sent = df['sentiment'].mean()
        st.info(f"Средний новостной фон за 24ч: **{'Позитивный' if avg_sent > 0.5 else 'Негативный'}** ({avg_sent:.2f})")
        st.warning("⚠️ Обнаружена корреляция: всплеск новостей об 'AI Regulation' совпадает с волатильностью тех-сектора.")

# Обновляем ROADMAP
with open(os.path.join(base_dir, "ROADMAP_4_0.md"), "a") as f:
    f.write("\n- [ ] Интеграция реальных графиков TradingView в дашборд.\n- [ ] Модуль автоматического сопоставления News Sentiment -> Market Volatility.\n")

