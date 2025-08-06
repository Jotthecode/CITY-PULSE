import streamlit as st
import pandas as pd
import datetime

# Import utility functions
from utils.weather import get_current_weather, get_monthly_weather
from utils.tourist import get_recommendations
from utils.air_quality import get_air_quality, describe_aqi, create_air_quality_charts
from utils.crime import get_crime_news
from utils.chatbot import search_google
from config import CITY_COORDS

# Page configuration
st.set_page_config(page_title="City Pulse", layout="wide")

st.title("City Pulse 🌆")
city = st.selectbox("Select a City", list(CITY_COORDS.keys()))

if city:
    lat = CITY_COORDS[city]["lat"]
    lon = CITY_COORDS[city]["lon"]

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    tabs = st.tabs([
        "🌦 Weather", 
        "🫁 Air Quality", 
        "🏖 Tourist Info", 
        "🚨 Crime News", 
        "📊 Trends", 
        "🤖 CityBot"
    ]) 

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

        with st.spinner("Fetching air quality data..."):
            air_quality = get_air_quality(city)

        if "error" in air_quality:
            st.error(air_quality["error"])
        else:
            st.markdown(f"### AQI Level: {air_quality['aqi']} - **{describe_aqi(air_quality['aqi'])}**")

            components = air_quality["components"]
            comp_df = pd.DataFrame(list(components.items()), columns=["Pollutant", "Value"])
            comp_df["Pollutant"] = comp_df["Pollutant"].str.upper()

            with st.expander("Pollutant Details Table (μg/m³)"):
                st.table(comp_df)

            # Visualizations
            create_air_quality_charts(comp_df)

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

    # --- CityBot Chat Tab ---
    with tabs[5]:
        st.header("🤖 Search CityBot")
        user_input = st.chat_input("Ask a question (e.g., top cafes, weekend events)")

        if user_input:
            st.session_state.search_history.append({"role": "user", "text": user_input})

            with st.spinner("Searching Google..."):
                answer = search_google(user_input)

            st.session_state.search_history.append({"role": "bot", "text": answer})

        for msg in st.session_state.search_history:
            if msg["role"] == "user":
                st.chat_message("user").markdown(msg["text"])
            else:
                st.chat_message("assistant").markdown(msg["text"])
