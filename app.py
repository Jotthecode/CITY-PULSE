import streamlit as st
import pandas as pd
import datetime

# Import your existing utility functions
from utils.weather import get_current_weather, get_monthly_weather
from utils.tourist import get_recommendations
from config import CITY_COORDS
from utils.air_quality import get_air_quality
from utils.crime import get_crime_news
from utils.chatbot import search_google


st.set_page_config(page_title="City Pulse", layout="wide")

st.title("City Pulse 🌆")

search = st.text_input("Search for a city", placeholder="Type to search or leave empty to see full list below")
st.markdown("### Or select from dropdown below")
# Full city list (sorted)
all_cities = sorted(CITY_COORDS.keys())

# If user typed something, filter the list
if search:
    filtered_cities = [city for city in all_cities if search.lower() in city.lower()]
    
    if filtered_cities:
        city = st.selectbox("Select cities", filtered_cities)
    else:
        st.warning("No matching cities found.")
        city = None
        
else:
    city = st.selectbox("Select a city", all_cities)

# Use selected_city if available
if city:
    lat = CITY_COORDS[city]["lat"]
    lon = CITY_COORDS[city]["lon"]
    st.success(f"Showing results for {city}")


    # --- Initialize chat history in session state ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Create tabs
    tabs = st.tabs(["Weather", "Air Quality", "Tourist Info", "Crime News", "Trends", "Find with City Pulse"]) 

    # --- Existing Tabs (No changes needed for these sections) ---
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
    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    for msg in st.session_state.search_history:
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["text"])
        else:
            st.chat_message("assistant").markdown(msg["text"])
else:
    st.info("Please select a valid city to see the information.")

