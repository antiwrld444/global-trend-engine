import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GTOE | Market Opportunities", layout="wide")

st.title("🌍 Global Trend & Opportunity Engine")
st.markdown("### Аналитический дашборд для поиска рыночных возможностей")

def get_data():
    conn = sqlite3.connect("/root/projects/global-trend-engine/data/trends.db")
    df = pd.read_sql_query("SELECT * FROM trends ORDER BY timestamp DESC", conn)
    # Рассчитываем скоринг на лету для дашборда
    df['opportunity_score'] = (df['sentiment'] * 0.6) + (df['mentions_count'] * 0.4)
    return df

data = get_data()

if data.empty:
    st.warning("База данных пуста. Запустите пайплайн для сбора данных.")
else:
    # Метрики
    total_trends = len(data)
    avg_sentiment = data['sentiment'].mean()
    
    m1, m2 = st.columns(2)
    m1.metric("Всего трендов", total_trends)
    m2.metric("Средний Sentiment", f"{avg_sentiment:.2f}")

    # Основная таблица
    st.subheader("🔥 Топ рыночных возможностей")
    st.dataframe(data[['title', 'category', 'opportunity_score', 'timestamp']].sort_values(by='opportunity_score', ascending=False), use_container_width=True)

    # Визуализация по категориям
    st.subheader("📊 Распределение по нишам")
    fig = px.pie(data, names='category', values='opportunity_score', hole=0.3)
    st.plotly_express.plotly_chart(fig, use_container_width=True)

st.sidebar.info("Разработано Михал Палычем для BI-аналитики.")
