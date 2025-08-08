import streamlit as st
import pandas as pd
import datetime

# Import your existing utility functions
from utils.weather import get_current_weather, get_monthly_weather
from utils.tourist import get_recommendations
from utils.city_api import search_cities
from utils.air_quality import get_air_quality
from utils.crime import get_crime_news
from utils.emergency import get_osm_places
from utils.chatbot import search_google

st.set_page_config(page_title="City Pulse", layout="wide")

st.title("City Pulse 🌆")
city_query = st.text_input("🔍 Type a city name:")

if city_query:
    matched_cities = search_cities(city_query)

    if matched_cities:
        city_labels = [c['label'] for c in matched_cities]
        selected_label = st.selectbox("Select a city from matches:", city_labels)
        selected_city = next(c for c in matched_cities if c['label'] == selected_label)
        city = selected_label
        lat, lon = selected_city["lat"], selected_city["lon"]

        st.success(f"📍 You selected: {selected_label} — Lat: {lat}, Lon: {lon}")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        tabs = st.tabs(["Weather", "Air Quality", "Tourist Info", "Crime News","Emergency Services","Trends", "Find with City Pulse"])

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
            st.header("🚨 Find Emergency Services Near You")

            if city and lat and lon:
                st.subheader(f"City: {city}")

                st.subheader("🏥 Hospitals")
                hospitals = get_osm_places("hospital", lat, lon)
                if hospitals:
                   for h in hospitals:
                        st.markdown(f"- {h['display_name']} ([📍Map](https://www.google.com/maps?q={h['lat']},{h['lon']}))")
                else:
                    st.info("No hospitals found nearby.")

                st.subheader("🚓 Police Stations")
                police = get_osm_places("police station", lat, lon)
                if police:
                    for p in police:
                        st.markdown(f"- {p['display_name']} ([📍Map](https://www.google.com/maps?q={p['lat']},{p['lon']}))")
                else:
                    st.info("No police stations found nearby.")

                st.subheader("🚒 Fire Stations")
                fire = get_osm_places("fire station", lat, lon)
                if fire:
                    for f in fire:
                        st.markdown(f"- {f['display_name']} ([📍Map](https://www.google.com/maps?q={f['lat']},{f['lon']}))")
                else:
                    st.info("No fire stations found nearby.")
            else:
                st.warning("Please select a city in the search box above.")            

        with tabs[5]:
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

        with tabs[6]:
            st.header("🤖 Search CityBot")

            if "search_history" not in st.session_state:
                st.session_state.search_history = []

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

    else:
        st.warning("No matching cities found.")
