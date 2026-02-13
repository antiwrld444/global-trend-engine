import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Добавляем путь для импорта наших модулей
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.analytics.anomaly_detector import AnomalyDetector

st.set_page_config(page_title="GTOE | Market Opportunities", layout="wide")

st.title("🌍 Global Trend & Opportunity Engine")
st.markdown("### Интерактивный аналитический дашборд")

DB_PATH = "/root/projects/global-trend-engine/data/trends.db"

def get_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame(), pd.DataFrame()
    
    conn = sqlite3.connect(DB_PATH)
    
    # Основные данные трендов
    df_trends = pd.read_sql_query("SELECT * FROM trends ORDER BY timestamp DESC", conn)
    if not df_trends.empty:
        df_trends['opportunity_score'] = (df_trends['sentiment'] * 0.6) + (df_trends['mentions_count'] * 0.4)
    
    # История изменений
    df_history = pd.read_sql_query("""
        SELECT h.timestamp, h.score, t.title, t.category 
        FROM trend_history h 
        JOIN trends t ON h.trend_id = t.id 
        ORDER BY h.timestamp ASC
    """, conn)
    
    conn.close()
    return df_trends, df_history

df_trends, df_history = get_data()

if df_trends.empty:
    st.warning("База данных пуста или отсутствует. Запустите пайплайн для сбора данных.")
else:
    # Определение Breakouts
    detector = AnomalyDetector(threshold=1.5)
    breakout_titles = detector.detect_breakouts(df_trends)
    
    df_trends['is_breakout'] = df_trends['title'].isin(breakout_titles)

    # Метрики
    total_trends = len(df_trends)
    avg_sentiment = df_trends['sentiment'].mean()
    breakouts_count = len(breakout_titles)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Всего трендов", total_trends)
    m2.metric("Средний Sentiment", f"{avg_sentiment:.2f}")
    m3.metric("Breakouts 🚀", breakouts_count)

    # Секция Breakouts
    if breakouts_count > 0:
        st.subheader("🚀 Текущие Breakouts (Аномальный рост)")
        cols = st.columns(min(breakouts_count, 4))
        for i, title in enumerate(breakout_titles[:4]):
            with cols[i % 4]:
                st.info(f"**{title}**")

    # Основной контент
    tab1, tab2, tab3 = st.tabs(["🔥 Топ Трендов", "📈 История Динамики", "📊 Аналитика Ниш"])

    with tab1:
        st.subheader("Ранжированный список возможностей")
        
        # Добавляем иконку ракеты к названиям Breakout трендов для таблицы
        display_df = df_trends.copy()
        display_df['title'] = display_df.apply(
            lambda x: f"🚀 {x['title']}" if x['is_breakout'] else x['title'], axis=1
        )
        
        st.dataframe(
            display_df[['title', 'category', 'opportunity_score', 'mentions_count', 'timestamp']]
            .sort_values(by='opportunity_score', ascending=False), 
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.subheader("Динамика изменения Score")
        if not df_history.empty:
            # Выберем топ-10 трендов по последнему скору для графика истории
            top_titles = df_trends.nlargest(10, 'opportunity_score')['title'].tolist()
            history_plot_df = df_history[df_history['title'].isin(top_titles)]
            
            fig_line = px.line(
                history_plot_df, 
                x='timestamp', 
                y='score', 
                color='title',
                title="История Score для Топ-10 трендов",
                labels={'score': 'Sentiment Score', 'timestamp': 'Дата/Время'},
                template="plotly_dark"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("История изменений пока не накоплена.")

    with tab3:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### Распределение по нишам")
            fig_pie = px.sunburst(
                df_trends, 
                path=['category', 'title'], 
                values='opportunity_score',
                color='opportunity_score',
                color_continuous_scale='RdBu',
                title="Иерархия трендов по категориям"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_right:
            st.markdown("#### Sentiment vs Популярность")
            fig_scatter = px.scatter(
                df_trends, 
                x='mentions_count', 
                y='sentiment', 
                size='opportunity_score', 
                color='category',
                hover_name='title',
                title="Связь упоминаний и настроения"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("Разработано для BI-аналитики трендов. (v2.0 Visual Upgrade)")
