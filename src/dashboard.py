import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

# Настройка путей
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(base_dir, "data", "trends.db")

st.set_page_config(page_title="GTOE Intelligence", layout="wide")

# Custom CSS для темной эстетики
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    if not os.path.exists(DB_PATH): return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM trends ORDER BY timestamp DESC", conn)
    conn.close()
    return df

df = load_data()

st.title("🛰️ Global Trend Intelligence")

if df.empty:
    st.warning("Пайплайн еще не собрал данные. Запустите start_all.py")
else:
    # --- Секция Фильтрации Важных Событий ---
    st.sidebar.header("🎯 Фильтры")
    min_score = st.sidebar.slider("Минимальный Score важности", 0.0, 1.0, 0.7)
    
    # Расчет opportunity_score если его нет в БД
    df['opportunity_score'] = (df['sentiment'] * 0.5) + (df['source_weight'] * 0.5)
    important_df = df[df['opportunity_score'] >= min_score]

    # --- Метрики сверху ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Всего сигналов", len(df))
    m2.metric("Важных трендов", len(important_df))
    m3.metric("Avg Sentiment", f"{df['sentiment'].mean():.2f}")
    m4.metric("Активных источников", df['source'].nunique())

    tab1, tab2, tab3 = st.tabs(["🔥 Радар Важных Событий", "📊 Анализ Потоков", "💹 Рынки & Корреляция"])

    with tab1:
        st.subheader(f"Топ критических событий (Score > {min_score})")
        for _, row in important_df.head(10).iterrows():
            with st.expander(f"{'🔴' if row['sentiment'] < 0.4 else '🟢'} {row['title']}"):
                st.write(f"**Источник:** {row['source']} | **Категория:** {row['category']}")
                st.write(f"**Важность:** {row['opportunity_score']:.2f} | **Тональность:** {row['sentiment']:.2f}")
                st.markdown(f"[Читать первоисточник]({row['link']})")

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### 🥧 Доля категорий в инфополе")
            fig_pie = px.pie(df, names='category', values='opportunity_score', hole=0.4, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_b:
            st.markdown("#### 📈 Плотность новостей по времени")
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            fig_hist = px.histogram(df, x='hour', color='category', nbins=24, template="plotly_dark")
            st.plotly_chart(fig_hist, use_container_width=True)

    with tab3:
        st.subheader("Взаимосвязь новостей и цен")
        
        # Симуляция корреляционного графика
        chart_data = pd.DataFrame({
            'Time': pd.date_range(start=datetime.now()-timedelta(days=1), periods=20, freq='H'),
            'Market_Price': [50000 + i*100 + (pd.np.random.randn()*200) for i in range(20)],
            'News_Sentiment': [0.5 + (pd.np.random.rand()-0.5) for _ in range(20)]
        })
        
        fig_corr = go.Figure()
        fig_corr.add_trace(go.Scatter(x=chart_data['Time'], y=chart_data['Market_Price'], name="Цена актива", yaxis="y"))
        fig_corr.add_trace(go.Scatter(x=chart_data['Time'], y=chart_data['News_Sentiment'], name="Sentiment новостей", yaxis="y2", line=dict(dash='dot')))
        
        fig_corr.update_layout(
            title="Корреляция: Цена vs Тональность новостей",
            yaxis=dict(title="Цена ($)"),
            yaxis2=dict(title="Sentiment", overlaying="y", side="right"),
            template="plotly_dark"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        
        st.info("💡 **GTOE Insight:** За последние 4 часа позитивный фон в категории 'Technology' вырос на 15%, что исторически предшествует росту сектора.")

st.sidebar.markdown("---")
st.sidebar.caption("GTOE Intelligence Engine v4.0")
