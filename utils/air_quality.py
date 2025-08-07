import requests
import os

# Load API key
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 1. --- Fetch Air Quality Data ---
def get_air_quality(city):
    geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
    geo_params = {"q": city, "limit": 1, "appid": OPENWEATHER_API_KEY}

    try:
        geo_res = requests.get(geocoding_url, params=geo_params, timeout=5)
        geo_res.raise_for_status()
        geo_data = geo_res.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch coordinates: {str(e)}"}

    if not geo_data:
        return {"error": "City not found"}

    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]

    air_url = "http://api.openweathermap.org/data/2.5/air_pollution"
    air_params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}

    try:
        air_res = requests.get(air_url, params=air_params, timeout=5)
        air_res.raise_for_status()
        air_data = air_res.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch air quality: {str(e)}"}

    if "list" not in air_data:
        return {"error": "No air quality data available"}

    air_info = air_data["list"][0]
    return {
        "aqi": air_info["main"]["aqi"],
        "components": air_info["components"]
    }


# 2. --- AQI Description ---
def describe_aqi(aqi):
    levels = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor"
    }
    return levels.get(aqi, "Unknown")


# 3. --- Visualization + Explanations ---
def create_air_quality_charts(comp_df):
    import streamlit as st
    import seaborn as sns
    import matplotlib.pyplot as plt
    import plotly.express as px
    import pandas as pd

    st.subheader("📊 Pollutant Concentration Chart")
    fig_bar = px.bar(comp_df,
                     x="Pollutant",
                     y="Value",
                     color="Value",
                     color_continuous_scale="YlOrRd",
                     text=comp_df["Value"].apply(lambda x: f"{x:.1f} μg/m³"),
                     title="Concentration of Major Pollutants",
                     labels={"Value": "Concentration (μg/m³)"})
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14),
        title_x=0.5,
        height=500
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### 🧪 Pollutant Breakdown")
    pollutant_info = {
        "CO": "Carbon Monoxide – Can reduce oxygen delivery to body tissues.",
        "NO": "Nitric Oxide – Contributes to ground-level ozone and smog.",
        "NO2": "Nitrogen Dioxide – Irritates airways and worsens asthma.",
        "O3": "Ozone – Good in upper atmosphere, harmful at ground level.",
        "SO2": "Sulfur Dioxide – Harmful to respiratory system, causes acid rain.",
        "PM2_5": "Fine Particulate Matter – Penetrates lungs deeply; harmful.",
        "PM10": "Coarse Particulate Matter – Can affect lungs and heart.",
        "NH3": "Ammonia – Released by agriculture, can irritate eyes and lungs."
    }

    for _, row in comp_df.iterrows():
        name = row["Pollutant"]
        val = row["Value"]
        description = pollutant_info.get(name, "No description available.")
        st.markdown(f"**{name}**: `{val} μg/m³` — {description}")

    st.subheader("🌡️ Heatmap of Pollutants")
    fig, ax = plt.subplots(figsize=(10, 1.5))
    sns.heatmap([comp_df["Value"].values],
                annot=True, fmt=".1f", cmap="RdYlGn_r",
                cbar=False,
                xticklabels=comp_df["Pollutant"].values,
                yticklabels=["μg/m³"],
                ax=ax)
    ax.set_title("Pollutant Intensity Heatmap", fontsize=14)
    st.pyplot(fig)

    st.markdown("""
    ### 🔍 Heatmap Interpretation
    - Colors represent **pollutant severity**: green is lower, red is higher.
    - Each cell shows pollutant amount in **micrograms per cubic meter (μg/m³)**.
    - Watch out for **PM2.5**, **NO₂**, and **SO₂** — they can impact heart & lung health.
    - Heatmap helps identify **critical pollutants at a glance**.
    """)