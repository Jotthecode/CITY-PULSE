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

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/CITY-PULSE.git
cd CITY-PULSE
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your API keys:
   ```bash
   # Required API Keys
   OPENWEATHER_API_KEY=your_openweathermap_api_key_here
   VISUALCROSSING_API_KEY=your_visualcrossing_api_key_here
   NEWS_API_KEY=your_news_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   CSE_ID=your_custom_search_engine_id_here
   ```

### 4. Get Your API Keys
- **OpenWeatherMap API**: [Get free API key](https://openweathermap.org/api)
- **Visual Crossing API**: [Get free API key](https://www.visualcrossing.com/weather-api)
- **News API**: [Get free API key](https://newsapi.org/)
- **Google Custom Search API**: [Get API key](https://developers.google.com/custom-search/v1/introduction)
- **Custom Search Engine**: [Create CSE](https://cse.google.com/)

### 5. Run the Application
```bash
streamlit run app.py
```

---

## 🚨 Security Notice

This application requires API keys to function properly. **Never commit your `.env` file or expose your API keys publicly**. The `.env` file is already included in `.gitignore` to prevent accidental commits.

---
