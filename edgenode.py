import time
import requests
import json
import pandas as pd
import random
from datetime import datetime, timedelta

# --- CONFIGURATION ---
NTFY_TOPIC = "lohith_agri_demo"  # Subscribe on your phone's ntfy app
CHECK_INTERVAL_SECONDS = 15

def get_forecast_and_weather():
    lat, lon = 13.6288, 79.4192  # Tirupati base coordinates
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,precipitation,wind_gusts_10m,weather_code"
        f"&hourly=soil_moisture_0_to_7cm"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max"
        f"&timezone=auto"
    )
    try:
        res = requests.get(url, timeout=8).json()
        
        # Current conditions + sensor noise
        base_temp = res['current']['temperature_2m']
        base_moisture = res['hourly']['soil_moisture_0_to_7cm'][0]
        weather_code = res['current']['weather_code']
        
        live_temp = round(base_temp + random.uniform(-0.3, 0.3), 1)
        live_moisture = round(base_moisture + random.uniform(-0.02, 0.02), 3)
        
        # Extract 7-Day Forecast Data
        daily = res.get('daily', {})
        forecast_7d = []
        for i in range(len(daily.get('time', []))):
            forecast_7d.append({
                "date": daily['time'][i],
                "temp_max": daily['temperature_2m_max'][i],
                "temp_min": daily['temperature_2m_min'][i],
                "rain_sum": daily['precipitation_sum'][i],
                "rain_prob": daily.get('precipitation_probability_max', [0]*7)[i],
                "wind_max": daily['wind_speed_10m_max'][i],
                "code": daily['weather_code'][i]
            })
            
        return {
            "temp": live_temp,
            "rain_24h": res['current']['precipitation'],
            "wind_gust": res['current']['wind_gusts_10m'],
            "soil_moisture": abs(live_moisture),
            "weather_code": weather_code,
            "forecast_7d": forecast_7d
        }
    except Exception as e:
        # Dynamic 7-day fallback if Wi-Fi blocks the API
        today = datetime.now()
        fallback_forecast = []
        for d in range(7):
            f_date = (today + timedelta(days=d)).strftime("%Y-%m-%d")
            fallback_forecast.append({
                "date": f_date,
                "temp_max": round(32.0 + random.uniform(-1, 2), 1),
                "temp_min": round(23.0 + random.uniform(-1, 1), 1),
                "rain_sum": round(random.uniform(0, 15) if d != 3 else 48.5, 1), # Simulated rain on Day 4
                "rain_prob": random.randint(10, 40) if d != 3 else 85,
                "wind_max": round(random.uniform(12, 25), 1),
                "code": 3 if d != 3 else 95
            })
            
        return {
            "temp": round(30.0 + random.uniform(-0.5, 0.5), 1),
            "rain_24h": 0.0,
            "wind_gust": round(10.0 + random.uniform(-1.5, 1.5), 1),
            "soil_moisture": round(0.25 + random.uniform(-0.02, 0.02), 3),
            "weather_code": 0,
            "forecast_7d": fallback_forecast
        }

def get_soil():
    try:
        df = pd.read_csv("kaggle_crop_data.csv")
        sample = df[df['label'] == 'rice'].sample(1).iloc[0]
        return {"N": float(sample['N']), "P": float(sample['P']), "K": float(sample['K']), "ph": float(sample['ph'])}
    except:
        return {"N": 80.0, "P": 40.0, "K": 40.0, "ph": 6.5}

print("📡 Agri-Sentinel Edge Daemon active. Monitoring field sensors...")
print(f"🔔 Live ntfy alerts routed to: ntfy.sh/{NTFY_TOPIC}")

while True:
    weather = get_forecast_and_weather()
    soil = get_soil()
    
    # 1. Check for Advance Forecast Threat (Next 3 days)
    advance_warning = None
    for day in weather['forecast_7d'][1:4]:
        if day['rain_sum'] >= 35.0:
            advance_warning = f"ADVANCE ALERT: Heavy rain expected on {day['date']} ({day['rain_sum']}mm). Plan field drainage now!"
            break
        elif day['wind_max'] >= 45.0:
            advance_warning = f"ADVANCE ALERT: High winds expected on {day['date']} ({day['wind_max']} km/h). Protect flowering crops!"
            break
    
    weather['advance_warning'] = advance_warning

    # 2. Life Safety & Real-Time Alert Logic
    lightning_active = weather['weather_code'] in [95, 96, 99]
    demo_trigger = random.randint(1, 10) # 10% chance for demo alert
    
    alert_msg = None
    if lightning_active or demo_trigger == 1:
        weather['lightning_strike_km'] = round(random.uniform(1.2, 5.0), 1)
        alert_msg = f"⚡ DANGER: Lightning detected {weather['lightning_strike_km']}km away! Stop work and seek indoor shelter immediately."
    else:
        weather['lightning_strike_km'] = None
        if weather['soil_moisture'] < 0.15:
            alert_msg = "CRITICAL: Severe moisture deficiency detected. Initiate irrigation."
        elif weather['rain_24h'] > 40:
            alert_msg = "WARNING: Waterlogging threat from heavy rainfall. Inspect field trenches."

    # 3. Write data bridge for Streamlit
    current_state = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "weather": weather,
        "soil": soil
    }
    
    with open("live_farm_data.json", "w") as f:
        json.dump(current_state, f)
        
    print(f"[{current_state['timestamp']}] Sync: Moisture={weather['soil_moisture']}, Temp={weather['temp']}C")
    
    # 4. Dispatch Push Notification if triggered
    if alert_msg:
        print(f"⚠️ Triggering phone alert via ntfy...")
        headers = {"Title": "AgriAI Field Alert", "Priority": "urgent", "Tags": "warning,rotating_light"}
        try:
            requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=alert_msg.encode('utf-8'), headers=headers, timeout=6)
            print("✅ Alert delivered. Sleeping 60 seconds to avoid spam...")
            time.sleep(60)
        except Exception as e:
            print(f"❌ Network dispatch failed: {e}")
            time.sleep(CHECK_INTERVAL_SECONDS)
    else:
        time.sleep(CHECK_INTERVAL_SECONDS)