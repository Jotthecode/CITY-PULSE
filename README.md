# 🌆 City Pulse — Your Ultimate City Insights Dashboard

City Pulse is a sleek, real-time dashboard built with **Streamlit** that provides everything you need to know about any city — from live weather updates and air quality to crime news, tourist recommendations, Google Trends analysis, and even an AI-powered chatbot that lets you search through Google.

---

## 🚀 Features

### ✅ Live City Intelligence:
- **🌤️ Weather Data**: Real-time temperature, humidity, and weather conditions.
- **🌧️ Monthly Trends**: Average monthly temperatures, precipitation, and humidity.
- **🌬️ Air Quality Index (AQI)**: Live air quality breakdown with pollutant analysis.

### 🌍 City Exploration:
- **🏞️ Tourist Attractions**: Top-rated places to visit in the city, powered by Google Places API.
- **📰 Crime News**: Recent city-specific crime headlines, updated in real time.

### 📈 Trends & Analytics:
- **Google Trends Integration**: Visualize how interest in your city is trending globally over time.

### 🤖 Ask CityBot (Chatbot):
- Built-in chatbot that leverages Google Search to answer queries about the city.
- Ask things like: `Top cafes near the city center`, `Free events this weekend`, `Nightlife recommendations`, etc.

---

## 💻 Tech Stack

- **Frontend**: Streamlit
- **Backend/APIs**:
  - [OpenWeatherMap API](https://openweathermap.org/api) for Weather and AQI
  - [Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview)
  - [Google Trends via Pytrends](https://github.com/GeneralMills/pytrends)
  - News API for crime-related news
  - Custom chatbot using Google Search integration
- **Others**: Pandas, Requests, Python, HTML/CSS (via Streamlit components)

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 📦 Installation

```bash
git clone https://github.com/your-username/city-pulse.git
cd city-pulse
pip install -r requirements.txt
streamlit run app.py
