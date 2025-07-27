import streamlit as st
import pandas as pd
import datetime
import asyncio

# Import your existing utility functions
from utils.weather import get_current_weather, get_monthly_weather
from utils.tourist import get_recommendations
from config import CITY_COORDS
from utils.air_quality import get_air_quality
from utils.crime import get_crime_news
from utils.chatbot import search_google
# Import the CityPulseAnimations class
from utils.city_pulse_animation import CityPulseAnimations
import random

st.set_page_config(page_title="City Pulse", layout="wide")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_city_pulse_data(city, lat, lon):
    """Get city pulse data synchronously for Streamlit"""
    try:
        # Set up API keys (replace with your actual keys)
        api_keys = {
            'openweather': 'YOUR_OPENWEATHER_API_KEY_HERE',  # Get from https://openweathermap.org/api
            # 'weatherapi': 'YOUR_WEATHERAPI_KEY_HERE',  # Optional
            # 'aqicn': 'YOUR_AQICN_API_KEY_HERE'  # Optional
        }
        
        # Run the async function
        async def fetch_data():
            async with CityPulseAnimations(api_keys) as city_pulse:
                return await city_pulse.update_city_data(city, lat, lon)
        
        # Execute the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        city_data = loop.run_until_complete(fetch_data())
        loop.close()
        
        return city_data
    except Exception as e:
        st.error(f"Error fetching city pulse data: {e}")
        return None

st.title("City Pulse 🌆")
city = st.selectbox("Select a City", list(CITY_COORDS.keys()))

if city:
    lat = CITY_COORDS[city]["lat"]
    lon = CITY_COORDS[city]["lon"]

    # --- Initialize chat history in session state ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # --- City Pulse Section ---
    st.header(f"🎯 City Pulse for {city}")
    
    city_pulse_data = get_city_pulse_data(city, lat, lon)
    
    if city_pulse_data:
        pulse_params = city_pulse_data.get('pulse_params', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Pulse Color", pulse_params.get('color', '#00ff7f'))
            
        with col2:
            st.metric("Pulse Speed", f"{pulse_params.get('speed', 1.0):.1f}x")
            
        with col3:
            st.metric("Pulse Pattern", pulse_params.get('pattern', 'normal').title())
            
        with col4:
            st.metric("Pulse Intensity", f"{pulse_params.get('intensity', 0.7):.1f}")
        
        # Show pulse visualization
        pulse_color = pulse_params.get('color', '#00ff7f')
        pulse_speed = pulse_params.get('speed', 1.0)
        pulse_intensity = pulse_params.get('intensity', 0.7)
        pulse_pattern = pulse_params.get('pattern', 'normal')
        
        st.markdown(f"""
        <div class="pulse-container" style="text-align: center; margin: 20px 0;">
            <div class="city-pulse" style="
                width: 120px; 
                height: 120px; 
                background: radial-gradient(circle, {pulse_color} 0%, rgba(0,255,127,0.3) 70%, transparent 100%);
                border-radius: 50%; 
                margin: 20px auto;
                animation: cityPulse {2.0/pulse_speed:.1f}s ease-in-out infinite;
                box-shadow: 0 0 30px {pulse_color};
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
            ">
                ❤️
            </div>
            <p style="margin-top: 10px; font-style: italic; color: #666;">
                Pattern: {pulse_pattern.title()} | Reflecting real-time city conditions
            </p>
        </div>
        
        <style>
        @keyframes cityPulse {{
            0%, 100% {{ 
                transform: scale(1);
                box-shadow: 0 0 20px {pulse_color};
            }}
            50% {{ 
                transform: scale({1 + pulse_intensity * 0.3});
                box-shadow: 0 0 40px {pulse_color};
            }}
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Show detailed pulse information
        with st.expander("🔍 Pulse Details"):
            weather_data = city_pulse_data.get('weather', {})
            current_weather = weather_data.get('current', {})
            air_quality = weather_data.get('air_quality', {})
            crime_data = city_pulse_data.get('crime', {})
            tourism_data = city_pulse_data.get('tourism', {})
            
            st.write("**Pulse Factors:**")
            st.write(f"🌡️ Temperature: {current_weather.get('temperature', 'N/A')}°C")
            st.write(f"🏭 Air Quality Index: {air_quality.get('aqi', 'N/A')}")
            st.write(f"🚨 Crime Risk Level: {crime_data.get('risk_level', 0.3):.1f}")
            st.write(f"🎯 Tourist Activity: {tourism_data.get('activity_level', 0.6):.1f}")
            
            st.info("💡 **How it works:** Color reflects air quality, speed varies with weather severity, intensity is influenced by crime data, and size changes with tourist activity levels.")
    
    else:
        st.warning("⚠️ City Pulse data unavailable. Please check your API keys or try again later.")

    # Create tabs
    tabs = st.tabs(["Weather", "Air Quality", "Tourist Info", "Crime News", "Trends", "Find with City Pulse"]) 

    # --- Weather Tab ---
    with tabs[0]:
        st.header(f"Current Weather in {city}")
        weather = get_current_weather(city, lat, lon)
        if "error" in weather:
            st.error(weather["error"])
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Temperature (°C)", weather["temperature"])
            col2.metric("Feels Like (°C)", weather["feels_like"])
            col3.metric("Humidity (%)", weather["humidity"])
            st.write(f"**Description:** {weather['description'].capitalize()}")
            st.image(f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png")

        monthly_weather = get_monthly_weather(city)
        if isinstance(monthly_weather, list) and monthly_weather:
            st.subheader("Monthly Weather Summary")
            df_monthly = pd.DataFrame(monthly_weather)
            df_monthly = df_monthly.rename(columns={
                "month": "Month",
                "avg_temp": "Avg Temp (°C)",
                "humidity": "Humidity (%)",
                "precip": "Precipitation (mm)"
            })
            st.dataframe(df_monthly)

    # --- Air Quality Tab ---
    with tabs[1]:
        st.header(f"Air Quality in {city}")
        air_quality = get_air_quality(city)
        if "error" in air_quality:
            st.error(air_quality["error"])
        else:
            aqi_level = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
            st.markdown(f"### AQI Level: {air_quality['aqi']} - **{aqi_level.get(air_quality['aqi'], 'Unknown')}**")
            with st.expander("Pollutant Details (μg/m³)"):
                comp_df = pd.DataFrame(list(air_quality["components"].items()), columns=["Pollutant", "Value"])
                comp_df["Pollutant"] = comp_df["Pollutant"].str.upper()
                st.table(comp_df)

    # --- Tourist Info Tab ---
    with tabs[2]:
        st.header(f"Tourist Recommendations in {city}")
        tourist_data = get_recommendations(city)
        places = tourist_data.get("places", [])
        if places and not places[0].get("error"):
            with st.expander("Top Tourist Places"):
                for place in places:
                    st.markdown(f"**{place.get('name', 'N/A')}**")
                    st.write(f"Address: {place.get('address', 'N/A')}")
                    if place.get('rating'):
                        st.write(f"Rating: {place.get('rating', 'N/A')}")
                    st.markdown("---")
        else:
            if places and places[0].get("error"):
                st.error(f"Error fetching tourist places: {places[0]['error']}")
            else:
                st.info("No tourist places data available or could not be fetched.")

    # --- Crime News Tab ---
    with tabs[3]:
        st.header(f"Recent Crime News in {city}")
        crime_news = get_crime_news(city)
        if crime_news and not crime_news[0].get("error"):
            with st.expander("Show Crime News Articles"):
                for news in crime_news:
                    st.markdown(f"**[{news['title']}]({news['url']})**")
                    st.write(news["description"])
                    st.write(f"*Published at: {news['publishedAt']}*")
                    st.markdown("---")
        else:
            if crime_news and crime_news[0].get("error"):
                st.error(crime_news[0]["error"])
            else:
                st.info("No crime news found.")

    # --- Trends Tab ---
    with tabs[4]:
        st.header("How Popular is Your City? 📈")
        trends = tourist_data.get("trends", [])
        if trends and not trends[0].get("error"):
            dates = [trend["date"] for trend in trends]
            interests = [trend["interest"] for trend in trends]
            df_trends = pd.DataFrame({"Date": pd.to_datetime(dates), "Interest": interests})
            df_trends = df_trends.set_index("Date")
            st.line_chart(df_trends)
        else:
            if trends and trends[0].get("error"):
                st.error(trends[0]["error"])
            else:
                st.info("No trends data available.")

    # --- Chatbot Tab ---
    with tabs[5]:
        st.header("🤖 Search CityBot")

        if "search_history" not in st.session_state:
            st.session_state.search_history = []
        
        user_input = st.chat_input("Ask a question (e.g., top cafes, weekend events)")

        if user_input:
            st.session_state.search_history.append({"role": "user", "text": user_input})

            with st.spinner("Searching Google..."):
                answer = search_google(user_input)

            st.session_state.search_history.append({"role": "bot", "text": answer})

        # Display chat messages
        for msg in st.session_state.search_history:
            if msg["role"] == "user":
                st.chat_message("user").markdown(msg["text"])
            else:
                st.chat_message("assistant").markdown(msg["text"])