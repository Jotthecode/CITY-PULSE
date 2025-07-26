import streamlit as st
import pandas as pd
import datetime
import time
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

from utils.weather import get_current_weather, get_monthly_weather
from utils.tourist import get_recommendations
from config import CITY_COORDS
from utils.air_quality import get_air_quality
from utils.crime import get_crime_news
from utils.chatbot import search_google

st.set_page_config(page_title="City Pulse", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    .main > div {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Enhanced Pulse Animation */
    .pulse {
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-left: 10px;
        border-radius: 50%;
        background: linear-gradient(45deg, #00c851, #007e33);
        box-shadow: 0 0 0 rgba(0, 200, 81, 0.7);
        animation: enhanced-pulse 2s infinite;
        position: relative;
    }
    
    .pulse::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: rgba(0, 200, 81, 0.3);
        transform: translate(-50%, -50%);
        animation: ripple 2s infinite;
    }

    @keyframes enhanced-pulse {
        0% { 
            box-shadow: 0 0 0 0 rgba(0, 200, 81, 0.7),
                        0 0 0 0 rgba(0, 200, 81, 0.4);
        }
        40% { 
            box-shadow: 0 0 0 15px rgba(0, 200, 81, 0),
                        0 0 0 30px rgba(0, 200, 81, 0);
        }
        100% { 
            box-shadow: 0 0 0 0 rgba(0, 200, 81, 0),
                        0 0 0 0 rgba(0, 200, 81, 0);
        }
    }
    
    @keyframes ripple {
        0% { transform: translate(-50%, -50%) scale(0); opacity: 1; }
        100% { transform: translate(-50%, -50%) scale(4); opacity: 0; }
    }

    /* Animated Weather Card */
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
        animation: slideInFromLeft 0.8s ease-out;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
    }
    
    .weather-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }

    @keyframes slideInFromLeft {
        0% { transform: translateX(-100%); opacity: 0; }
        100% { transform: translateX(0); opacity: 1; }
    }

    /* Enhanced Weather Icon Animation */
    .weather-icon {
        animation: weather-bounce 2s ease-in-out infinite;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
        transition: transform 0.3s ease;
    }
    
    .weather-icon:hover {
        transform: scale(1.1) rotate(5deg);
    }

    @keyframes weather-bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }

    /* AQI Gauge Animation */
    .aqi-container {
        background : #1e1e1e;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        animation: slideInFromRight 0.8s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .aqi-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        animation: shimmer 3s infinite;
    }

    @keyframes slideInFromRight {
        0% { transform: translateX(100%); opacity: 0; }
        100% { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(30deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(30deg); }
    }

    /* Tourist Places Card */
    .tourist-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
        animation: fadeInUp 0.6s ease-out;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .tourist-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    @keyframes fadeInUp {
        0% { transform: translateY(30px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }

    /* Chat Animation */
    .chat-message {
        animation: messageSlideIn 0.5s ease-out;
        margin: 10px 0;
    }
    
    @keyframes messageSlideIn {
        0% { transform: translateX(-20px); opacity: 0; }
        100% { transform: translateX(0); opacity: 1; }
    }

    .typing-indicator {
        display: inline-block;
        animation: typing 1.5s infinite;
        color: #667eea;
        font-weight: 600;
    }

    @keyframes typing {
        0%, 60%, 100% { opacity: 1; }
        30% { opacity: 0.4; }
    }

    /* News Card Animation */
    .news-card {
        background: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
        animation: slideInScale 0.7s ease-out;
        transition: transform 0.3s ease;
    }
    
    .news-card:hover {
        transform: scale(1.02);
    }
    
    @keyframes slideInScale {
        0% { transform: scale(0.8); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    
    @keyframes bounceIn {
        0% { transform: scale(0.3); opacity: 0; }
        50% { transform: scale(1.1); }
        70% { transform: scale(0.9); }
        100% { transform: scale(1); opacity: 1; }
    }

    /* Tab Animation */
    .stTabs [data-baseweb="tab-list"] {
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: white;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255,255,255,0.2);
        transform: translateY(-1px);
    }

    /* Loading Animation */
    .loading-dots {
        display: inline-block;
        position: relative;
        width: 80px;
        height: 80px;
    }
    
    .loading-dots div {
        position: absolute;
        top: 33px;
        width: 13px;
        height: 13px;
        border-radius: 50%;
        background: #667eea;
        animation-timing-function: cubic-bezier(0, 1, 1, 0);
    }
    
    .loading-dots div:nth-child(1) {
        left: 8px;
        animation: loading1 0.6s infinite;
    }
    
    .loading-dots div:nth-child(2) {
        left: 8px;
        animation: loading2 0.6s infinite;
    }
    
    .loading-dots div:nth-child(3) {
        left: 32px;
        animation: loading2 0.6s infinite;
    }
    
    .loading-dots div:nth-child(4) {
        left: 56px;
        animation: loading3 0.6s infinite;
    }
    
    @keyframes loading1 {
        0% { transform: scale(0); }
        100% { transform: scale(1); }
    }
    
    @keyframes loading3 {
        0% { transform: scale(1); }
        100% { transform: scale(0); }
    }
    
    @keyframes loading2 {
        0% { transform: translate(0, 0); }
        100% { transform: translate(24px, 0); }
    }

    /* Glassmorphism Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 20px;
        margin: 10px 0;
        animation: glassSlideIn 0.8s ease-out;
    }
    
    @keyframes glassSlideIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Title with Animation
st.markdown("<h1 style='text-align:center;'>🌃 City Pulse</h1>", unsafe_allow_html=True)

st.markdown("<div style='text-align: center; margin-bottom: 30px;'><div class='pulse'></div> <span style='color: #667eea; font-weight: 600;'>Real-time Data Active</span></div>", unsafe_allow_html=True)

# Enhanced City Selection with Animation
col_select1, col_select2, col_select3 = st.columns([1, 2, 1])
with col_select2:
    city = st.selectbox(
        "Select a City", 
        list(CITY_COORDS.keys()),
        help="Choose a city to explore real-time data"
    )

if city:
    lat = CITY_COORDS[city]["lat"]
    lon = CITY_COORDS[city]["lon"]

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Enhanced Tabs with Icons
    tabs = st.tabs([
        "Weather", 
        "Air Quality", 
        "Tourist Info", 
        "Crime News", 
        "Trends", 
        "City Assistant"
    ])

    with tabs[0]:
        st.markdown(f"<h2>Current Weather in {city}</h2>", unsafe_allow_html=True)
        
        # Create weather container with loading animation
        weather_container = st.container()
        with weather_container:
            with st.spinner("Fetching weather data..."):
                weather = get_current_weather(city, lat, lon)
                time.sleep(0.5)  # Brief pause for animation effect
        
        if "error" in weather:
            st.error(f"❌ {weather['error']}")
        else:
            # Enhanced Weather Cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="weather-card">
                    <h3 style="margin: 0; font-size: 1.2rem;">Temperature</h3>
                    <h1 style="margin: 10px 0; font-size: 2.5rem;">{weather["temperature"]}°C</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="weather-card">
                    <h3 style="margin: 0; font-size: 1.2rem;">Feels Like</h3>
                    <h1 style="margin: 10px 0; font-size: 2.5rem;">{weather["feels_like"]}°C</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="weather-card">
                    <h3 style="margin: 0; font-size: 1.2rem;">Humidity</h3>
                    <h1 style="margin: 10px 0; font-size: 2.5rem;">{weather["humidity"]}%</h1>
                </div>
                """, unsafe_allow_html=True)
            
            # Weather Description with Icon
            st.markdown(f"""
            <div class="weather-card">
                <div style="display: flex; align-items: center; justify-content: center;">
                    <img class='weather-icon' src='http://openweathermap.org/img/wn/{weather['icon']}@4x.png' width='150'>
                    <div style="margin-left: 20px;">
                        <h2 style="margin: 0; color: white;">{weather['description']}</h2>
                        <p style="margin: 5px 0; opacity: 0.8;">Current conditions in {city}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Enhanced Monthly Weather Chart
        monthly_weather = get_monthly_weather(city)
        if isinstance(monthly_weather, list) and monthly_weather:
            st.markdown("<h3 style='color: #667eea; margin-top: 30px;'>Monthly Weather Trends</h3>", unsafe_allow_html=True)
            
            df_monthly = pd.DataFrame(monthly_weather)
            
            # Create animated plotly chart
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Temperature Trend', 'Humidity Levels', 'Precipitation', 'Weather Overview'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Temperature line
            fig.add_trace(
                go.Scatter(
                    x=df_monthly['month'], 
                    y=df_monthly['avg_temp'],
                    mode='lines+markers',
                    name='Temperature (°C)',
                    line=dict(color='#ff6b6b', width=3),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )
            
            # Humidity bar
            fig.add_trace(
                go.Bar(
                    x=df_monthly['month'], 
                    y=df_monthly['humidity'],
                    name='Humidity (%)',
                    marker_color='#4ecdc4'
                ),
                row=1, col=2
            )
            
            # Precipitation area
            fig.add_trace(
                go.Scatter(
                    x=df_monthly['month'], 
                    y=df_monthly['precip'],
                    fill='tonexty',
                    mode='lines',
                    name='Precipitation (mm)',
                    line=dict(color='#45b7d1')
                ),
                row=2, col=1
            )
            
            # Combined overview
            fig.add_trace(
                go.Scatter(
                    x=df_monthly['month'], 
                    y=df_monthly['avg_temp'],
                    mode='lines+markers',
                    name='Temp Overview',
                    line=dict(color='#96ceb4', width=2)
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                height=600,
                showlegend=True,
                title_text="Weather Analytics Dashboard",
                font=dict(family="Poppins, sans-serif")
            )
            
            st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.markdown(f"<h2>Air Quality in {city}</h2>", unsafe_allow_html=True)
        
        with st.spinner("Analyzing air quality..."):
            air_quality = get_air_quality(city)
            time.sleep(0.3)
        
        if "error" in air_quality:
            st.error(f"❌ {air_quality['error']}")
        else:
            aqi_level = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
            aqi_colors = {1: "#00e400", 2: "#ffff00", 3: "#ff7e00", 4: "#ff0000", 5: "#8f3f97"}
            
            # AQI Gauge Chart
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = air_quality['aqi'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Air Quality Index"},
                delta = {'reference': 3},
                gauge = {
                    'axis': {'range': [None, 5]},
                    'bar': {'color': aqi_colors.get(air_quality['aqi'], "#gray")},
                    'steps': [
                        {'range': [0, 1], 'color': "#e8f5e8"},
                        {'range': [1, 2], 'color': "#fff8e1"},
                        {'range': [2, 3], 'color': "#fff3e0"},
                        {'range': [3, 4], 'color': "#ffebee"},
                        {'range': [4, 5], 'color': "#f3e5f5"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 4
                    }
                }
            ))
            
            fig_gauge.update_layout(
                height=400,
                font=dict(family="Poppins, sans-serif")
            )
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col2:
                st.markdown(f"""
                <div class="aqi-container">
                    <h3 style="margin: 0; text-align: center;">AQI Status</h3>
                    <h1 style="margin: 10px 0; text-align: center; font-size: 3rem;">{air_quality['aqi']}</h1>
                    <h2 style="margin: 0; text-align: center; color: {aqi_colors.get(air_quality['aqi'], '#gray')};">{aqi_level.get(air_quality['aqi'], 'Unknown')}</h2>
                    <div class='pulse' style="margin: 20px auto; display: block;"></div>
                </div>
                """, unsafe_allow_html=True)

            # Pollutant Details with Interactive Chart
            st.markdown("<h3>Pollutant Breakdown</h3>", unsafe_allow_html=True)
            
            pollutants = air_quality["components"]
            pollutant_df = pd.DataFrame(list(pollutants.items()), columns=["Pollutant", "Value"])
            pollutant_df["Pollutant"] = pollutant_df["Pollutant"].str.upper()
            
            fig_pollutants = px.bar(
                pollutant_df, 
                x="Pollutant", 
                y="Value",
                color="Value",
                color_continuous_scale="Viridis",
                title="Pollutant Concentrations (μg/m³)"
            )
            fig_pollutants.update_layout(
                xaxis_title="Pollutants",
                yaxis_title="Concentration (μg/m³)",
                font=dict(family="Poppins, sans-serif")
            )
            st.plotly_chart(fig_pollutants, use_container_width=True)

    with tabs[2]:
        st.markdown(f"<h2>Tourist Recommendations in {city}</h2>", unsafe_allow_html=True)
        
        with st.spinner("Discovering amazing places..."):
            tourist_data = get_recommendations(city)
            time.sleep(0.4)
        
        places = tourist_data.get("places", [])
        if places and not places[0].get("error"):
            st.markdown("<h3 style='color: #667eea;'>Top Tourist Destinations</h3>", unsafe_allow_html=True)
            
            for i, place in enumerate(places[:8]): 
                st.markdown(f"""
                <div class="tourist-card" style="animation-delay: {i * 0.1}s;">
                    <h3 style="margin: 0 0 10px 0; color: white;">{place.get('name', 'N/A')}</h3>
                    <p style="margin: 5px 0; opacity: 0.9;">{place.get('address', 'N/A')}</p>
                    {f"<h4 style='margin: 5px 0; opacity: 0.9;'>Rating: {place.get('rating', 'N/A')}/5</h4>" if place.get('rating') else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            if places and places[0].get("error"):
                st.error(f"❌ Error fetching tourist places: {places[0]['error']}")
            else:
                st.info("No tourist places data available at the moment.")

    with tabs[3]:
        st.markdown(f"<h2>Recent Crime News in {city}</h2>", unsafe_allow_html=True)
        
        with st.spinner("Gathering latest news..."):
            crime_news = get_crime_news(city)
            time.sleep(0.3)
        
        if crime_news and not crime_news[0].get("error"):
            st.markdown("<h3 style='color: #667eea;'>Latest Crime Reports</h3>", unsafe_allow_html=True)
            
            for i, news in enumerate(crime_news[:6]):  # Limit to 6 articles
                st.markdown(f"""
                <div class="news-card" style="animation-delay: {i * 0.1}s;">
                    <h4 style="margin: 0 0 10px 0;"><a href="{news['url']}" target="_blank" style="color: white; text-decoration: none;">{news['title']}</a></h4>
                    <p style="margin: 5px 0; opacity: 0.9;">📢 {news['description'][:200]}{'...' if len(news['description']) > 200 else ''}</p>
                    <p style="margin: 5px 0; opacity: 0.7; font-size: 0.9rem;">{news['publishedAt']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            if crime_news and crime_news[0].get("error"):
                st.error(f"❌ {crime_news[0]['error']}")
            else:
                st.info("📰 No recent crime news found.")

    with tabs[4]:
        st.markdown("<h2 style='color: #667eea;'>How Popular is Your City?</h2>", unsafe_allow_html=True)
        
        trends = tourist_data.get("trends", [])
        if trends and not trends[0].get("error"):
            # Create animated trend chart
            dates = [trend["date"] for trend in trends]
            interests = [trend["interest"] for trend in trends]
            
            fig_trends = go.Figure()
            fig_trends.add_trace(go.Scatter(
                x=dates,
                y=interests,
                mode='lines+markers',
                name='Interest Level',
                line=dict(color='#667eea', width=4),
                marker=dict(size=10, color='#764ba2'),
                fill='tonexty',
                fillcolor='rgba(102, 126, 234, 0.1)'
            ))
            
            fig_trends.update_layout(
                title=f"Tourist Interest Trends for {city}",
                xaxis_title="Date",
                yaxis_title="Interest Level",
                height=500,
                font=dict(family="Poppins, sans-serif"),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_trends, use_container_width=True)
            
            # Add trend insights
            avg_interest = np.mean(interests)
            max_interest = max(interests)
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: #667eea;">Trend Insights</h4>
                <p>Average Interest Level: <strong>{avg_interest:.1f}</strong></p>
                <p>Peak Interest: <strong>{max_interest}</strong></p>
                <p>Tracking Period: Last 7 days</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            if trends and trends[0].get("error"):
                st.error(f"❌ {trends[0]['error']}")
            else:
                st.info("No trends data available at the moment.")

    with tabs[5]:
        st.markdown("<h2>City Assistant</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666; margin-bottom: 20px;'>Ask me anything about your city - restaurants, events, attractions, and more!</p>", unsafe_allow_html=True)

        if "search_history" not in st.session_state:
            st.session_state.search_history = []

        # Chat interface
        user_input = st.chat_input("Ask me about restaurants, events, attractions...")

        if user_input:
            st.session_state.search_history.append({"role": "user", "text": user_input})
            
            # Show typing indicator
            typing_placeholder = st.empty()
            typing_placeholder.markdown('<div class="typing-indicator">Assistant is thinking...</div>', unsafe_allow_html=True)
            
            with st.spinner("Searching for information..."):
                time.sleep(1)  # Simulate thinking time
                answer = search_google(user_input)
            
            typing_placeholder.empty()
            st.session_state.search_history.append({"role": "bot", "text": answer})

        # Display chat history with animations
        for i, msg in enumerate(st.session_state.search_history):
            if msg["role"] == "user":
                st.chat_message("user").markdown(f'<div class="chat-message">{msg["text"]}</div>', unsafe_allow_html=True)
            else:
                st.chat_message("assistant").markdown(f'<div class="chat-message">{msg["text"]}</div>', unsafe_allow_html=True)

        # Quick action buttons
        st.markdown("<h4 style='color: #667eea;'>Quick Questions</h4>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🍕 Best Restaurants", use_container_width=True):
                st.session_state.search_history.append({"role": "user", "text": f"best restaurants in {city}"})
                with st.spinner("Finding great restaurants..."):
                    answer = search_google(f"best restaurants in {city}")
                st.session_state.search_history.append({"role": "bot", "text": answer})
                st.rerun()
        
        with col2:
            if st.button("🎉 Weekend Events", use_container_width=True):
                st.session_state.search_history.append({"role": "user", "text": f"weekend events in {city}"})
                with st.spinner("Discovering events..."):
                    answer = search_google(f"weekend events in {city}")
                st.session_state.search_history.append({"role": "bot", "text": answer})
                st.rerun()
        
        with col3:
            if st.button("☕ Coffee Shops", use_container_width=True):
                st.session_state.search_history.append({"role": "user", "text": f"best coffee shops in {city}"})
                with st.spinner("Finding cozy cafes..."):
                    answer = search_google(f"best coffee shops in {city}")
                st.session_state.search_history.append({"role": "bot", "text": answer})
                st.rerun()
        
        with col4:
            if st.button("🛍️ Shopping", use_container_width=True):
                st.session_state.search_history.append({"role": "user", "text": f"shopping places in {city}"})
                with st.spinner("Locating shopping areas..."):
                    answer = search_google(f"shopping places in {city}")
                st.session_state.search_history.append({"role": "bot", "text": answer})
                st.rerun()

# Sidebar with Real-time City Pulse
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h2 style="color: #667eea;">🌆 City Pulse Monitor</h2>
        <div class='pulse' style="margin: 20px auto; display: block;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Real-time data indicators
    if city:
        st.markdown(f"<h4 style='color: #667eea;'>📍 {city} Status</h4>", unsafe_allow_html=True)
        
        # Simulate real-time data updates
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        st.markdown(f"**Last Update:** {current_time}")
        
        # Data freshness indicators
        indicators = [
            ("Weather Data", "Fresh", "#00c851"),
            ("Air Quality", "Live", "#00c851"),
            ("News Feed", "Updated", "#ffa726"),
            ("Tourist Info", "Active", "#00c851"),
            ("Trends", "Real-time", "#00c851")
        ]
        
        for indicator, status, color in indicators:
            st.markdown(f"""
            <div style="
                background: #1e1e1e;
                padding: 10px;
                border-radius: 8px;
                margin: 5px 0;
                border-left: 4px solid {color};
            ">
                <span style="font-weight: 600;">{indicator}</span><br>
                <span style="color: {color}; font-size: 0.9rem;">● {status}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Auto-refresh toggle
        auto_refresh = st.toggle("🔄 Auto-refresh data", value=False)
        if auto_refresh:
            time.sleep(30)  # Refresh every 30 seconds
            st.rerun()
    
    # City statistics
    st.markdown("<h4 style='color: #667eea; margin-top: 30px;'>Quick Stats</h4>", unsafe_allow_html=True)
    if city and city in CITY_COORDS:
        coords = CITY_COORDS[city]
        st.markdown(f"""
        <div style="background: #1e1e1e;" class="glass-card">
            <p><strong>Coordinates:</strong><br>
            Lat: {coords['lat']}<br>
            Lon: {coords['lon']}</p>
            <p><strong>Local Time:</strong><br>{datetime.datetime.now().strftime('%I:%M %p')}</p>
            <p><strong>Date:</strong><br>{datetime.datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        """, unsafe_allow_html=True)

