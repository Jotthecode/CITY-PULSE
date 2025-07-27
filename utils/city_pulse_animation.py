import asyncio
import aiohttp
import json
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import colorsys
import aiohttp_cors

class CityPulseAnimations:
    """
    Real-time city pulse visualization system that creates dynamic animations
    based on weather, air quality, crime data, and tourist activity.
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        """
        Initialize the City Pulse system with API keys.
        
        Args:
            api_keys: Dictionary containing API keys for different services
                     - 'openweather': OpenWeatherMap API key
                     - 'aqicn': Air Quality API key (optional, has free tier)
                     - 'weatherapi': WeatherAPI.com key (optional)
        """
        self.api_keys = api_keys
        self.session = None
        self.city_data = {}
        self.pulse_state = {
            'color': '#00ff7f',  # Default green
            'speed': 1.0,        # Pulse speed multiplier
            'intensity': 0.7,    # Pulse intensity (0-1)
            'pattern': 'normal', # normal, erratic, calm, intense
            'size': 100,         # Base size in pixels
            'glow': 0.5         # Glow effect intensity
        }
        
        # Color mappings for different conditions
        self.aqi_colors = {
            1: '#00e400',  # Good - Green
            2: '#ffff00',  # Fair - Yellow  
            3: '#ff7e00',  # Moderate - Orange
            4: '#ff0000',  # Poor - Red
            5: '#8f3f97',  # Very Poor - Purple
            6: '#7e0023'   # Hazardous - Maroon
        }
        
        self.weather_patterns = {
            'clear': {'speed': 0.8, 'pattern': 'calm'},
            'clouds': {'speed': 1.0, 'pattern': 'normal'},
            'rain': {'speed': 1.5, 'pattern': 'erratic'},
            'thunderstorm': {'speed': 2.0, 'pattern': 'intense'},
            'snow': {'speed': 0.6, 'pattern': 'calm'},
            'mist': {'speed': 0.9, 'pattern': 'normal'},
            'fog': {'speed': 0.7, 'pattern': 'calm'}
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def get_weather_data(self, city: str, lat: float = None, lon: float = None) -> Dict:
        """
        Fetch comprehensive weather data using multiple APIs for redundancy.
        
        Args:
            city: City name
            lat: Latitude (optional)
            lon: Longitude (optional)
            
        Returns:
            Dictionary containing weather data
        """
        weather_data = {}
        
        try:
            # Try OpenWeatherMap first (most comprehensive)
            if 'openweather' in self.api_keys:
                weather_data = await self._get_openweather_data(city, lat, lon)
            
            # Fallback to Open-Meteo (free, no API key required)
            if not weather_data:
                weather_data = await self._get_open_meteo_data(lat or 0, lon or 0)
                
            # Add WeatherAPI.com data if available
            if 'weatherapi' in self.api_keys:
                additional_data = await self._get_weatherapi_data(city)
                weather_data.update(additional_data)
                
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            # Return default data to keep the system running
            weather_data = self._get_default_weather_data()
            
        return weather_data

    async def _get_openweather_data(self, city: str, lat: float = None, lon: float = None) -> Dict:
        """Fetch data from OpenWeatherMap API."""
        api_key = self.api_keys['openweather']
        base_url = "https://api.openweathermap.org/data/2.5"
        
        # Get coordinates if not provided
        if not lat or not lon:
            geo_url = f"{base_url}/weather?q={city}&appid={api_key}&units=metric"
        else:
            geo_url = f"{base_url}/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            
        async with self.session.get(geo_url) as response:
            if response.status == 200:
                current_data = await response.json()
                lat, lon = current_data['coord']['lat'], current_data['coord']['lon']
                
                # Get detailed forecast
                forecast_url = f"{base_url}/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
                async with self.session.get(forecast_url) as forecast_response:
                    forecast_data = await forecast_response.json() if forecast_response.status == 200 else {}
                
                # Get air pollution data
                air_url = f"{base_url}/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
                async with self.session.get(air_url) as air_response:
                    air_data = await air_response.json() if air_response.status == 200 else {}
                
                return self._process_openweather_data(current_data, forecast_data, air_data)
        
        return {}

    async def _get_open_meteo_data(self, lat: float, lon: float) -> Dict:
        """Fetch data from Open-Meteo API (free, no key required)."""
        base_url = "https://api.open-meteo.com/v1"
        
        # Current weather and forecast
        weather_url = f"{base_url}/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
        
        # Air quality
        air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"
        
        weather_data = {}
        air_quality_data = {}
        
        try:
            async with self.session.get(weather_url) as response:
                if response.status == 200:
                    weather_data = await response.json()
                    
            async with self.session.get(air_url) as response:
                if response.status == 200:
                    air_quality_data = await response.json()
                    
        except Exception as e:
            print(f"Error fetching Open-Meteo data: {e}")
            
        return self._process_open_meteo_data(weather_data, air_quality_data)

    async def _get_weatherapi_data(self, city: str) -> Dict:
        """Fetch data from WeatherAPI.com."""
        api_key = self.api_keys['weatherapi']
        base_url = "https://api.weatherapi.com/v1"
        
        current_url = f"{base_url}/current.json?key={api_key}&q={city}&aqi=yes"
        forecast_url = f"{base_url}/forecast.json?key={api_key}&q={city}&days=7&aqi=yes&alerts=yes"
        
        try:
            async with self.session.get(forecast_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_weatherapi_data(data)
        except Exception as e:
            print(f"Error fetching WeatherAPI data: {e}")
            
        return {}

    def _process_openweather_data(self, current: Dict, forecast: Dict, air: Dict) -> Dict:
        """Process OpenWeatherMap data into standardized format."""
        processed = {
            'current': {
                'temperature': current.get('main', {}).get('temp', 0),
                'feels_like': current.get('main', {}).get('feels_like', 0),
                'humidity': current.get('main', {}).get('humidity', 0),
                'pressure': current.get('main', {}).get('pressure', 1013),
                'description': current.get('weather', [{}])[0].get('description', ''),
                'main': current.get('weather', [{}])[0].get('main', ''),
                'icon': current.get('weather', [{}])[0].get('icon', ''),
                'wind_speed': current.get('wind', {}).get('speed', 0),
                'wind_direction': current.get('wind', {}).get('deg', 0),
                'clouds': current.get('clouds', {}).get('all', 0),
                'visibility': current.get('visibility', 10000) / 1000,  # Convert to km
                'uv_index': 0  # Not available in current weather
            },
            'location': {
                'name': current.get('name', ''),
                'country': current.get('sys', {}).get('country', ''),
                'lat': current.get('coord', {}).get('lat', 0),
                'lon': current.get('coord', {}).get('lon', 0),
                'timezone': current.get('timezone', 0)
            },
            'forecast': [],
            'air_quality': {}
        }
        
        # Process forecast data
        if forecast and 'list' in forecast:
            for item in forecast['list'][:40]:  # 5 days * 8 (3-hour intervals)
                processed['forecast'].append({
                    'datetime': datetime.fromtimestamp(item['dt']),
                    'temperature': item['main']['temp'],
                    'description': item['weather'][0]['description'],
                    'main': item['weather'][0]['main'],
                    'icon': item['weather'][0]['icon'],
                    'humidity': item['main']['humidity'],
                    'wind_speed': item['wind']['speed'],
                    'precipitation': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
                })
        
        # Process air quality data
        if air and 'list' in air:
            air_info = air['list'][0]
            processed['air_quality'] = {
                'aqi': air_info['main']['aqi'],
                'co': air_info['components']['co'],
                'no2': air_info['components']['no2'],
                'o3': air_info['components']['o3'],
                'so2': air_info['components']['so2'],
                'pm2_5': air_info['components']['pm2_5'],
                'pm10': air_info['components']['pm10'],
                'nh3': air_info['components']['nh3']
            }
            
        return processed

    def _process_open_meteo_data(self, weather: Dict, air: Dict) -> Dict:
        """Process Open-Meteo data into standardized format."""
        if not weather or 'current' not in weather:
            return {}
            
        current = weather['current']
        processed = {
            'current': {
                'temperature': current.get('temperature_2m', 0),
                'feels_like': current.get('apparent_temperature', 0),
                'humidity': current.get('relative_humidity_2m', 0),
                'pressure': current.get('pressure_msl', 1013),
                'description': self._weather_code_to_description(current.get('weather_code', 0)),
                'main': self._weather_code_to_main(current.get('weather_code', 0)),
                'wind_speed': current.get('wind_speed_10m', 0),
                'wind_direction': current.get('wind_direction_10m', 0),
                'clouds': current.get('cloud_cover', 0),
                'visibility': 10,  # Default value
                'precipitation': current.get('precipitation', 0)
            },
            'forecast': [],
            'air_quality': {}
        }
        
        # Process air quality if available
        if air and 'current' in air:
            air_current = air['current']
            processed['air_quality'] = {
                'aqi': air_current.get('us_aqi', 1),
                'pm2_5': air_current.get('pm2_5', 0),
                'pm10': air_current.get('pm10', 0),
                'co': air_current.get('carbon_monoxide', 0),
                'no2': air_current.get('nitrogen_dioxide', 0),
                'so2': air_current.get('sulphur_dioxide', 0),
                'o3': air_current.get('ozone', 0)
            }
            
        return processed

    def _process_weatherapi_data(self, data: Dict) -> Dict:
        """Process WeatherAPI.com data into standardized format."""
        current = data.get('current', {})
        location = data.get('location', {})
        
        processed = {
            'current': {
                'temperature': current.get('temp_c', 0),
                'feels_like': current.get('feelslike_c', 0),
                'humidity': current.get('humidity', 0),
                'pressure': current.get('pressure_mb', 1013),
                'description': current.get('condition', {}).get('text', ''),
                'wind_speed': current.get('wind_kph', 0) / 3.6,  # Convert to m/s
                'wind_direction': current.get('wind_degree', 0),
                'clouds': current.get('cloud', 0),
                'visibility': current.get('vis_km', 10),
                'uv_index': current.get('uv', 0)
            },
            'location': {
                'name': location.get('name', ''),
                'country': location.get('country', ''),
                'lat': location.get('lat', 0),
                'lon': location.get('lon', 0)
            },
            'air_quality': {}
        }
        
        # Air quality data
        if 'air_quality' in current:
            aq = current['air_quality']
            processed['air_quality'] = {
                'co': aq.get('co', 0),
                'no2': aq.get('no2', 0),
                'o3': aq.get('o3', 0),
                'so2': aq.get('so2', 0),
                'pm2_5': aq.get('pm2_5', 0),
                'pm10': aq.get('pm10', 0),
                'us_epa_index': aq.get('us-epa-index', 1),
                'gb_defra_index': aq.get('gb-defra-index', 1)
            }
            
        return processed

    def _weather_code_to_description(self, code: int) -> str:
        """Convert WMO weather codes to descriptions."""
        descriptions = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
            55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            66: "Light freezing rain", 67: "Heavy freezing rain",
            71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
            77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
            82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        return descriptions.get(code, "Unknown")

    def _weather_code_to_main(self, code: int) -> str:
        """Convert WMO weather codes to main categories."""
        if code == 0 or code == 1:
            return "Clear"
        elif code <= 3:
            return "Clouds"
        elif code <= 48:
            return "Mist"
        elif code <= 67:
            return "Rain"
        elif code <= 86:
            return "Snow"
        elif code >= 95:
            return "Thunderstorm"
        return "Unknown"

    def _get_default_weather_data(self) -> Dict:
        """Return default weather data when APIs fail."""
        return {
            'current': {
                'temperature': 25,
                'feels_like': 25,
                'humidity': 60,
                'pressure': 1013,
                'description': 'Clear sky',
                'main': 'Clear',
                'wind_speed': 3,
                'wind_direction': 180,
                'clouds': 20,
                'visibility': 10
            },
            'air_quality': {'aqi': 2, 'pm2_5': 15, 'pm10': 25},
            'location': {'name': 'Unknown', 'country': 'Unknown'}
        }

    async def get_crime_data(self, lat: float, lon: float) -> Dict:
        """
        Fetch crime data for the location.
        Note: This is a placeholder implementation. Real crime APIs often require
        specific municipal or government API access.
        """
        try:
            # Simulated crime data - replace with actual API calls
            # You would integrate with local police APIs, CrimeoMeter, or similar services
            base_risk = 0.3  # Base crime risk level (0-1)
            
            # Simulate time-based crime variations
            current_hour = datetime.now().hour
            time_multiplier = 1.2 if 20 <= current_hour or current_hour <= 6 else 0.8
            
            crime_data = {
                'risk_level': min(base_risk * time_multiplier, 1.0),
                'incidents_24h': int(base_risk * 10),
                'trend': 'stable',  # increasing, decreasing, stable
                'categories': {
                    'theft': 0.4,
                    'assault': 0.2,
                    'vandalism': 0.3,
                    'other': 0.1
                }
            }
            
            return crime_data
            
        except Exception as e:
            print(f"Error fetching crime data: {e}")
            return {'risk_level': 0.3, 'incidents_24h': 3, 'trend': 'stable'}

    async def get_tourist_activity(self, city: str) -> Dict:
        """
        Estimate tourist activity based on various factors.
        This is a simplified implementation - real systems might use
        Google Places API, social media APIs, or tourism board data.
        """
        try:
            # Simulate tourist activity based on time and season
            now = datetime.now()
            
            # Seasonal multiplier
            seasonal_multiplier = {
                12: 0.8, 1: 0.6, 2: 0.7,  # Winter
                3: 0.9, 4: 1.1, 5: 1.2,   # Spring
                6: 1.4, 7: 1.5, 8: 1.3,   # Summer
                9: 1.1, 10: 1.0, 11: 0.9  # Fall
            }.get(now.month, 1.0)
            
            # Daily multiplier
            daily_multiplier = 1.3 if now.weekday() >= 5 else 1.0  # Weekend boost
            
            # Hourly pattern
            hourly_pattern = {
                range(6, 9): 0.7,    # Early morning
                range(9, 12): 1.1,   # Morning
                range(12, 17): 1.4,  # Afternoon
                range(17, 21): 1.2,  # Evening
                range(21, 24): 0.9,  # Night
                range(0, 6): 0.3     # Late night
            }
            
            hour_multiplier = 1.0
            for time_range, multiplier in hourly_pattern.items():
                if now.hour in time_range:
                    hour_multiplier = multiplier
                    break
            
            base_activity = 0.6
            activity_level = base_activity * seasonal_multiplier * daily_multiplier * hour_multiplier
            activity_level = min(activity_level, 1.0)
            
            tourist_data = {
                'activity_level': activity_level,
                'hotspots_active': int(activity_level * 15),
                'peak_hours': [10, 11, 14, 15, 16],
                'seasonal_trend': 'high' if seasonal_multiplier > 1.2 else 'medium' if seasonal_multiplier > 0.8 else 'low'
            }
            
            return tourist_data
            
        except Exception as e:
            print(f"Error calculating tourist activity: {e}")
            return {'activity_level': 0.6, 'hotspots_active': 8, 'seasonal_trend': 'medium'}

    def calculate_pulse_parameters(self, weather_data: Dict, crime_data: Dict, tourist_data: Dict) -> Dict:
        """
        Calculate pulse visualization parameters based on all data sources.
        
        Returns:
            Dictionary with pulse parameters: color, speed, intensity, pattern, size, glow
        """
        pulse_params = self.pulse_state.copy()
        
        # 1. Determine color based on air quality (primary factor)
        air_quality = weather_data.get('air_quality', {})
        aqi = air_quality.get('aqi', air_quality.get('us_epa_index', 2))
        
        if aqi <= 2:
            base_color = '#00ff7f'  # Good - Green
        elif aqi == 3:
            base_color = '#ffff00'  # Moderate - Yellow
        elif aqi == 4:
            base_color = '#ff7e00'  # Poor - Orange
        else:
            base_color = '#ff0000'  # Very Poor/Hazardous - Red
            
        pulse_params['color'] = base_color
        
        # 2. Adjust speed based on weather severity
        weather_main = weather_data.get('current', {}).get('main', '').lower()
        weather_config = self.weather_patterns.get(weather_main, {'speed': 1.0, 'pattern': 'normal'})
        
        speed = weather_config['speed']
        
        # Wind speed affects pulse speed
        wind_speed = weather_data.get('current', {}).get('wind_speed', 0)
        speed *= (1 + wind_speed / 50)  # Normalize wind effect
        
        # Temperature extremes affect speed
        temp = weather_data.get('current', {}).get('temperature', 20)
        if temp > 35 or temp < -10:  # Extreme temperatures
            speed *= 1.3
            
        pulse_params['speed'] = min(speed, 3.0)  # Cap at 3x speed
        
        # 3. Adjust intensity based on crime data
        crime_risk = crime_data.get('risk_level', 0.3)
        base_intensity = 0.7
        
        # Higher crime increases intensity (more urgent pulse)
        intensity_multiplier = 1 + (crime_risk * 0.5)
        pulse_params['intensity'] = min(base_intensity * intensity_multiplier, 1.0)
        
        # 4. Adjust pattern based on weather and crime
        if weather_main in ['thunderstorm', 'tornado']:
            pulse_params['pattern'] = 'intense'
        elif crime_risk > 0.7:
            pulse_params['pattern'] = 'erratic'
        elif weather_main in ['clear', 'snow'] and crime_risk < 0.3:
            pulse_params['pattern'] = 'calm'
        else:
            pulse_params['pattern'] = weather_config.get('pattern', 'normal')
            
        # 5. Adjust size based on tourist activity
        tourist_activity = tourist_data.get('activity_level', 0.6)
        base_size = 100
        size_multiplier = 0.8 + (tourist_activity * 0.4)  # 0.8x to 1.2x size
        pulse_params['size'] = int(base_size * size_multiplier)
        
        # 6. Adjust glow based on weather conditions
        clouds = weather_data.get('current', {}).get('clouds', 50)
        visibility = weather_data.get('current', {}).get('visibility', 10)
        
        glow_base = 0.5
        if visibility < 5:  # Poor visibility increases glow
            glow_base += 0.3
        if clouds > 80:  # Heavy clouds reduce glow
            glow_base -= 0.2
            
        pulse_params['glow'] = max(min(glow_base, 1.0), 0.1)
        
        return pulse_params

    def generate_css_animation(self, pulse_params: Dict) -> str:
        """
        Generate CSS animations based on pulse parameters.
        
        Returns:
            CSS string with keyframe animations
        """
        color = pulse_params['color']
        speed = pulse_params['speed']
        intensity = pulse_params['intensity']
        pattern = pulse_params['pattern']
        size = pulse_params['size']
        glow = pulse_params['glow']
        
        # Convert hex color to RGB for glow effects
        rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        glow_color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {glow})"
        
        # Base animation duration (inverse of speed)
        duration = max(2.0 / speed, 0.5)
        
        # Pattern-specific keyframes
        if pattern == 'calm':
            keyframes = f"""
            @keyframes cityPulse {{
                0%, 100% {{ 
                    transform: scale(1);
                    box-shadow: 0 0 {int(20 * glow)}px {glow_color};
                }}
                50% {{ 
                    transform: scale({1 + intensity * 0.1});
                    box-shadow: 0 0 {int(40 * glow)}px {glow_color};
                }}
            }}
            """
        elif pattern == 'erratic':
            keyframes = f"""
            @keyframes cityPulse {{
                0% {{ 
                    transform: scale(1);
                    box-shadow: 0 0 {int(20 * glow)}px {glow_color};
                }}
                25% {{ 
                    transform: scale({1 + intensity * 0.2});
                    box-shadow: 0 0 {int(60 * glow)}px {glow_color};
                }}
                50% {{ 
                    transform: scale({1 + intensity * 0.05});
                    box-shadow: 0 0 {int(30 * glow)}px {glow_color};
                }}
                75% {{ 
                    transform: scale({1 + intensity * 0.15});
                    box-shadow: 0 0 {int(50 * glow)}px {glow_color};
                }}
                100% {{ 
                    transform: scale(1);
                    box-shadow: 0 0 {int(20 * glow)}px {glow_color};
                }}
            }}
            """
        elif pattern == 'intense':
            keyframes = f"""
            @keyframes cityPulse {{
                0%, 100% {{ 
                    transform: scale(1);
                    box-shadow: 0 0 {int(30 * glow)}px {glow_color};
                }}
                50% {{ 
                    transform: scale({1 + intensity * 0.3});
                    box-shadow: 0 0 {int(80 * glow)}px {glow_color};
                }}
            }}
            @keyframes cityPulseGlow {{
                0%, 50%, 100% {{ opacity: 1; }}
                25%, 75% {{ opacity: 0.7; }}
            }}
            """
        else:  # normal
            keyframes = f"""
            @keyframes cityPulse {{
                0%, 100% {{ 
                    transform: scale(1);
                    box-shadow: 0 0 {int(25 * glow)}px {glow_color};
                }}
                50% {{ 
                    transform: scale({1 + intensity * 0.15});
                    box-shadow: 0 0 {int(50 * glow)}px {glow_color};
                }}
            }}
            """
            
        # Main pulse element styles
        pulse_styles = f"""
        .city-pulse {{
            width: {size}px;
            height: {size}px;
            background: radial-gradient(circle, {color} 0%, rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.8) 70%, transparent 100%);
            border-radius: 50%;
            animation: cityPulse {duration:.1f}s ease-in-out infinite;
            position: relative;
            margin: 20px auto;
        }}
        
        .city-pulse::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: {int(size * 0.6)}px;
            height: {int(size * 0.6)}px;
            background: {color};
            border-radius: 50%;
            opacity: 0.9;
        }}
        
        .city-pulse::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: {int(size * 1.5)}px;
            height: {int(size * 1.5)}px;
            border: 2px solid {color};
            border-radius: 50%;
            opacity: 0.3;
            animation: cityPulse {duration * 1.5:.1f}s ease-in-out infinite reverse;
        }}
        """
        
        return keyframes + pulse_styles

    def generate_javascript_controller(self, pulse_params: Dict) -> str:
        """
        Generate JavaScript code to control real-time pulse updates.
        
        Returns:
            JavaScript string for real-time control
        """
        return f"""
        class CityPulseController {{
            constructor() {{
                this.isActive = true;
                this.updateInterval = 60000; // Update every minute
                this.pulseElement = null;
                this.heartIcon = null;
                this.lastUpdate = 0;
                this.currentParams = {json.dumps(pulse_params)};
            }}
            
            init() {{
                this.pulseElement = document.querySelector('.city-pulse');
                this.heartIcon = document.querySelector('.pulse-heart');
                this.startRealTimeUpdates();
                this.addEventListeners();
            }}
            
            startRealTimeUpdates() {{
                setInterval(() => {{
                    if (this.isActive) {{
                        this.fetchAndUpdatePulse();
                    }}
                }}, this.updateInterval);
            }}
            
            async fetchAndUpdatePulse() {{
                try {{
                    // This would call your Python backend API
                    const response = await fetch('/api/city-pulse-update');
                    const newParams = await response.json();
                    this.updatePulseAnimation(newParams);
                }} catch (error) {{
                    console.log('Failed to update pulse data:', error);
                }}
            }}
            
            updatePulseAnimation(params) {{
                if (!this.pulseElement) return;
                
                // Update CSS custom properties for smooth transitions
                document.documentElement.style.setProperty('--pulse-color', params.color);
                document.documentElement.style.setProperty('--pulse-size', params.size + 'px');
                document.documentElement.style.setProperty('--pulse-speed', params.speed + 's');
                document.documentElement.style.setProperty('--pulse-intensity', params.intensity);
                document.documentElement.style.setProperty('--pulse-glow', params.glow);
                
                // Apply new animation class based on pattern
                this.pulseElement.className = `city-pulse pulse-${{params.pattern}}`;
                
                this.currentParams = params;
                this.lastUpdate = Date.now();
            }}
            
            addEventListeners() {{
                // Pause/resume on click
                if (this.pulseElement) {{
                    this.pulseElement.addEventListener('click', () => {{
                        this.togglePulse();
                    }});
                }}
                
                // Handle visibility changes
                document.addEventListener('visibilitychange', () => {{
                    this.isActive = !document.hidden;
                }});
            }}
            
            togglePulse() {{
                this.isActive = !this.isActive;
                if (this.pulseElement) {{
                    this.pulseElement.style.animationPlayState = this.isActive ? 'running' : 'paused';
                }}
            }}
            
            // Simulate real-time data changes for demo
            simulateDataChanges() {{
                const patterns = ['normal', 'calm', 'erratic', 'intense'];
                const colors = ['#00ff7f', '#ffff00', '#ff7e00', '#ff0000'];
                
                setInterval(() => {{
                    const randomPattern = patterns[Math.floor(Math.random() * patterns.length)];
                    const randomColor = colors[Math.floor(Math.random() * colors.length)];
                    const randomSpeed = 0.5 + Math.random() * 2;
                    const randomIntensity = 0.5 + Math.random() * 0.5;
                    
                    this.updatePulseAnimation({{
                        color: randomColor,
                        speed: randomSpeed,
                        intensity: randomIntensity,
                        pattern: randomPattern,
                        size: this.currentParams.size,
                        glow: this.currentParams.glow
                    }});
                }}, 10000); // Change every 10 seconds for demo
            }}
        }}
        
        // Initialize when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {{
            const pulseController = new CityPulseController();
            pulseController.init();
            
            // Enable simulation mode for demo (remove in production)
            // pulseController.simulateDataChanges();
        }});
        """

    async def update_city_data(self, city: str, lat: float = None, lon: float = None) -> Dict:
        """
        Main method to fetch all city data and update pulse parameters.
        
        Args:
            city: City name
            lat: Latitude (optional)
            lon: Longitude (optional)
            
        Returns:
            Complete city data with pulse parameters
        """
        # Fetch all data concurrently for better performance
        tasks = [
            self.get_weather_data(city, lat, lon),
            self.get_crime_data(lat or 0, lon or 0),
            self.get_tourist_activity(city)
        ]
        
        try:
            weather_data, crime_data, tourist_data = await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error fetching city data: {e}")
            # Use fallback data
            weather_data = self._get_default_weather_data()
            crime_data = {'risk_level': 0.3, 'incidents_24h': 3, 'trend': 'stable'}
            tourist_data = {'activity_level': 0.6, 'hotspots_active': 8, 'seasonal_trend': 'medium'}
        
        # Calculate pulse parameters
        pulse_params = self.calculate_pulse_parameters(weather_data, crime_data, tourist_data)
        
        # Store updated data
        self.city_data = {
            'city': city,
            'timestamp': datetime.now().isoformat(),
            'weather': weather_data,
            'crime': crime_data,
            'tourism': tourist_data,
            'pulse_params': pulse_params
        }
        
        return self.city_data

    def generate_complete_html(self, city_data: Dict) -> str:
        """
        Generate complete HTML page with real-time city pulse visualization.
        
        Args:
            city_data: Complete city data dictionary
            
        Returns:
            Complete HTML string
        """
        pulse_params = city_data.get('pulse_params', self.pulse_state)
        weather = city_data.get('weather', {}).get('current', {})
        location = city_data.get('weather', {}).get('location', {})
        air_quality = city_data.get('weather', {}).get('air_quality', {})
        
        css_animations = self.generate_css_animation(pulse_params)
        js_controller = self.generate_javascript_controller(pulse_params)
        
        # Get AQI level description
        aqi = air_quality.get('aqi', air_quality.get('us_epa_index', 2))
        aqi_descriptions = {
            1: "Good", 2: "Fair", 3: "Moderate", 
            4: "Poor", 5: "Very Poor", 6: "Hazardous"
        }
        aqi_desc = aqi_descriptions.get(aqi, "Unknown")
        
        # Status text based on multiple factors
        temp = weather.get('temperature', 0)
        humidity = weather.get('humidity', 0)
        description = weather.get('description', 'Unknown').title()
        
        status_parts = []
        if aqi <= 2:
            status_parts.append("Healthy")
        elif aqi >= 4:
            status_parts.append("Unhealthy")
        
        if temp > 30:
            status_parts.append("Hot")
        elif temp < 5:
            status_parts.append("Cold")
        
        if humidity > 80:
            status_parts.append("Humid")
        elif humidity < 30:
            status_parts.append("Dry")
            
        pulse_status = f"({aqi_desc} AQI: {aqi}), {description}, Intensity: {pulse_params['pattern'].title()}, Pattern: {pulse_params['pattern'].title()}"
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>City Pulse - {location.get('name', city_data.get('city', 'Unknown'))}</title>
            <style>
                :root {{
                    --pulse-color: {pulse_params['color']};
                    --pulse-size: {pulse_params['size']}px;
                    --pulse-speed: {2.0 / pulse_params['speed']:.1f}s;
                    --pulse-intensity: {pulse_params['intensity']};
                    --pulse-glow: {pulse_params['glow']};
                }}
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 20px;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                
                .city-name {{
                    font-size: 2.5rem;
                    font-weight: 300;
                    margin-bottom: 10px;
                }}
                
                .city-selector {{
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                    padding: 8px 16px;
                    color: white;
                    font-size: 16px;
                    margin-bottom: 20px;
                }}
                
                .pulse-container {{
                    background: rgba(0, 0, 0, 0.2);
                    border-radius: 20px;
                    padding: 40px;
                    margin: 20px 0;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    text-align: center;
                    min-width: 300px;
                }}
                
                .pulse-title {{
                    font-size: 1.8rem;
                    font-weight: bold;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                
                .pulse-status {{
                    font-size: 0.9rem;
                    opacity: 0.8;
                    margin-bottom: 30px;
                    line-height: 1.4;
                }}
                
                {css_animations}
                
                .pulse-heart {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 2rem;
                    animation: heartbeat 1s ease-in-out infinite;
                }}
                
                @keyframes heartbeat {{
                    0%, 100% {{ transform: translate(-50%, -50%) scale(1); }}
                    50% {{ transform: translate(-50%, -50%) scale(1.1); }}
                }}
                
                .weather-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                    width: 100%;
                    max-width: 800px;
                }}
                
                .weather-card {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 20px;
                    backdrop-filter: blur(5px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    text-align: center;
                }}
                
                .weather-card h3 {{
                    font-size: 0.9rem;
                    opacity: 0.7;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .weather-value {{
                    font-size: 1.8rem;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                
                .weather-unit {{
                    font-size: 0.8rem;
                    opacity: 0.7;
                }}
                
                .weather-icon {{
                    font-size: 2rem;
                    margin-bottom: 10px;
                }}
                
                .legend {{
                    margin-top: 30px;
                    text-align: center;
                    opacity: 0.8;
                    font-size: 0.8rem;
                    line-height: 1.6;
                }}
                
                .controls {{
                    margin-top: 20px;
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                    flex-wrap: wrap;
                }}
                
                .control-btn {{
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                    padding: 8px 16px;
                    color: white;
                    cursor: pointer;
                    font-size: 14px;
                    transition: all 0.3s ease;
                }}
                
                .control-btn:hover {{
                    background: rgba(255, 255, 255, 0.2);
                    transform: translateY(-2px);
                }}
                
                @media (max-width: 768px) {{
                    .city-name {{ font-size: 2rem; }}
                    .pulse-container {{ padding: 20px; margin: 10px; }}
                    .weather-grid {{ grid-template-columns: 1fr 1fr; gap: 15px; }}
                    .weather-card {{ padding: 15px; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 class="city-name">{location.get('name', city_data.get('city', 'Unknown')).upper()}</h1>
                <select class="city-selector" onchange="changeCity(this.value)">
                    <option value="itanagar">Itanagar</option>
                    <option value="mumbai">Mumbai</option>
                    <option value="delhi">Delhi</option>
                    <option value="bangalore">Bangalore</option>
                    <option value="kolkata">Kolkata</option>
                    <option value="chennai">Chennai</option>
                    <option value="hyderabad">Hyderabad</option>
                    <option value="pune">Pune</option>
                </select>
            </div>
            
            <div class="pulse-container">
                <h2 class="pulse-title">{location.get('name', city_data.get('city', 'Unknown'))}</h2>
                <p class="pulse-status">{pulse_status}</p>
                
                <div class="city-pulse" title="Click to pause/resume">
                    <div class="pulse-heart">❤️</div>
                </div>
                
                <div class="controls">
                    <button class="control-btn" onclick="togglePulse()">⏯️ Toggle</button>
                    <button class="control-btn" onclick="refreshData()">🔄 Refresh</button>
                    <button class="control-btn" onclick="showInfo()">ℹ️ Info</button>
                </div>
            </div>
            
            <div class="weather-grid">
                <div class="weather-card">
                    <div class="weather-icon">🌡️</div>
                    <h3>Temperature</h3>
                    <div class="weather-value">{weather.get('temperature', 0):.1f}</div>
                    <div class="weather-unit">°C</div>
                </div>
                
                <div class="weather-card">
                    <div class="weather-icon">💧</div>
                    <h3>Feels Like</h3>
                    <div class="weather-value">{weather.get('feels_like', 0):.1f}</div>
                    <div class="weather-unit">°C</div>
                </div>
                
                <div class="weather-card">
                    <div class="weather-icon">💨</div>
                    <h3>Humidity</h3>
                    <div class="weather-value">{weather.get('humidity', 0)}</div>
                    <div class="weather-unit">%</div>
                </div>
                
                <div class="weather-card">
                    <div class="weather-icon">🌬️</div>
                    <h3>Wind Speed</h3>
                    <div class="weather-value">{weather.get('wind_speed', 0):.1f}</div>
                    <div class="weather-unit">m/s</div>
                </div>
                
                <div class="weather-card">
                    <div class="weather-icon">🏭</div>
                    <h3>Air Quality</h3>
                    <div class="weather-value" style="color: {pulse_params['color']}">{aqi_desc}</div>
                    <div class="weather-unit">AQI: {aqi}</div>
                </div>
                
                <div class="weather-card">
                    <div class="weather-icon">👁️</div>
                    <h3>Visibility</h3>
                    <div class="weather-value">{weather.get('visibility', 10):.1f}</div>
                    <div class="weather-unit">km</div>
                </div>
            </div>
            
            <div class="legend">
                <strong>City Pulse Legend:</strong><br>
                🟢 Green: Good air quality, calm conditions<br>
                🟡 Yellow: Moderate air quality, normal activity<br>
                🟠 Orange: Poor air quality, increased activity<br>
                🔴 Red: Unhealthy conditions, high activity<br><br>
                
                <strong>Pulse Patterns:</strong><br>
                Calm: Gentle, slow pulse • Normal: Steady rhythm<br>
                Erratic: Irregular beats • Intense: Fast, strong pulse<br><br>
                
                Speed varies with weather severity • Size reflects tourist activity<br>
                Intensity influenced by crime data • Updates every minute
            </div>
            
            <script>
                {js_controller}
                
                function changeCity(city) {{
                    window.location.href = `?city=${{city}}`;
                }}
                
                function togglePulse() {{
                    const pulse = document.querySelector('.city-pulse');
                    const isRunning = pulse.style.animationPlayState !== 'paused';
                    pulse.style.animationPlayState = isRunning ? 'paused' : 'running';
                }}
                
                function refreshData() {{
                    window.location.reload();
                }}
                
                function showInfo() {{
                    const info = `
City Pulse Real-Time Data:

🏙️ Location: {location.get('name', 'Unknown')}, {location.get('country', 'Unknown')}
🌡️ Temperature: {weather.get('temperature', 0):.1f}°C (Feels like {weather.get('feels_like', 0):.1f}°C)
🌤️ Conditions: {description}
💨 Wind: {weather.get('wind_speed', 0):.1f} m/s
💧 Humidity: {weather.get('humidity', 0)}%
🏭 Air Quality: {aqi_desc} (AQI: {aqi})
👁️ Visibility: {weather.get('visibility', 10):.1f} km

🎯 Pulse Characteristics:
• Color: {pulse_params['color']} (Air Quality Based)
• Speed: {pulse_params['speed']:.1f}x (Weather Influenced)
• Pattern: {pulse_params['pattern'].title()} (Multi-factor)
• Intensity: {pulse_params['intensity']:.1f} (Crime Data)

📊 Data Sources:
• Weather: OpenWeatherMap / Open-Meteo
• Air Quality: Multiple AQI APIs
• Crime Data: Simulated (integrate local APIs)
• Tourist Activity: Calculated based on patterns

⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔄 Auto-refresh: Every 60 seconds
                    `;
                    alert(info);
                }}
                
                // Auto-refresh page every 5 minutes
                setTimeout(() => {{
                    window.location.reload();
                }}, 300000);
            </script>
        </body>
        </html>
        """
        
        return html_template

    async def run_city_pulse_server(self, city: str = "Itanagar", port: int = 8501):
        """
        Run a simple web server to serve the city pulse visualization.
        This method can be called to start the server.
        """
        from aiohttp import web
        import aiohttp_cors
        
        async def handle_city_pulse(request):
            city_param = request.query.get('city', city)
            
            # Get city coordinates (you might want to add a geocoding service)
            city_coords = {
                'itanagar': (27.0844, 93.6053),
                'mumbai': (19.0760, 72.8777),
                'delhi': (28.6139, 77.2090),
                'bangalore': (12.9716, 77.5946),
                'kolkata': (22.5726, 88.3639),
                'chennai': (13.0827, 80.2707),
                'hyderabad': (17.3850, 78.4867),
                'pune': (18.5204, 73.8567)
            }
            
            lat, lon = city_coords.get(city_param.lower(), (27.0844, 93.6053))
            
            city_data = await self.update_city_data(city_param, lat, lon)
            html_content = self.generate_complete_html(city_data)
            
            return web.Response(text=html_content, content_type='text/html')
        
        async def handle_api_update(request):
            city_param = request.query.get('city', city)
            city_coords = {
                'itanagar': (27.0844, 93.6053),
                'mumbai': (19.0760, 72.8777),
                'delhi': (28.6139, 77.2090),
                'bangalore': (12.9716, 77.5946),
                'kolkata': (22.5726, 88.3639),
                'chennai': (13.0827, 80.2707),
                'hyderabad': (17.3850, 78.4867),
                'pune': (18.5204, 73.8567)
            }
            
            lat, lon = city_coords.get(city_param.lower(), (27.0844, 93.6053))
            city_data = await self.update_city_data(city_param, lat, lon)
            
            return web.json_response(city_data['pulse_params'])
        
        app = web.Application()
        
        # Setup CORS
        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Routes
        app.router.add_get('/', handle_city_pulse)
        app.router.add_get('/api/city-pulse-update', handle_api_update)
        
        # Add CORS to all routes
        for route in list(app.router.routes()):
            cors.add(route)
        
        print(f"🎯 City Pulse Server starting on http://localhost:{port}")
        print(f"🌍 Default city: {city}")
        print(f"🔄 Real-time updates enabled")
        print(f"📊 Multi-source data integration active")
        
        return app


# Example usage and API key setup
def get_api_keys():
    """
    Set up your API keys here. Get free keys from:
    
    1. OpenWeatherMap: https://openweathermap.org/api
       - Free tier: 1000 calls/day
       - Provides weather + air quality data
    
    2. WeatherAPI.com: https://www.weatherapi.com/
       - Free tier: 1M calls/month
       - Comprehensive weather data
    
    3. Air Quality APIs:
       - AQICN: https://aqicn.org/api/ (free with registration)
       - Open-Meteo: https://open-meteo.com/ (completely free, no key needed)
    
    Note: The system works with fallbacks, so you can start with just one API key
    or even none (using Open-Meteo free service).
    """
    return {
        'openweather': 'YOUR_OPENWEATHER_API_KEY_HERE',
        'weatherapi': 'YOUR_WEATHERAPI_KEY_HERE',  # Optional
        'aqicn': 'YOUR_AQICN_API_KEY_HERE'  # Optional
    }


async def main():
    """
    Main function to run the City Pulse system.
    """
    api_keys = get_api_keys()
    
    async with CityPulseAnimations(api_keys) as city_pulse:
        # Test the system with Itanagar
        print("🚀 Testing City Pulse system...")
        
        city_data = await city_pulse.update_city_data("Itanagar", 27.0844, 93.6053)
        
        print(f"✅ Data fetched for {city_data['city']}")
        print(f"🌡️ Current temperature: {city_data['weather']['current']['temperature']}°C")
        print(f"🎨 Pulse color: {city_data['pulse_params']['color']}")
        print(f"⚡ Pulse speed: {city_data['pulse_params']['speed']:.1f}x")
        print(f"🔮 Pulse pattern: {city_data['pulse_params']['pattern']}")
        
        # Generate HTML file
        html_content = city_pulse.generate_complete_html(city_data)
        
        with open('city_pulse_demo.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("📄 Generated city_pulse_demo.html - Open this file in your browser!")
        
        # Optionally start the server
        # app = await city_pulse.run_city_pulse_server("Itanagar", 8501)
        # web.run_app(app, host='localhost', port=8501)


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())