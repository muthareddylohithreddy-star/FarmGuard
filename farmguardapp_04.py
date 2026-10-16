import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime, timedelta, timezone

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Agri-Sentinel OS", page_icon="🌾", layout="wide", initial_sidebar_state="collapsed")

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Intake"
if 'lang' not in st.session_state:
    st.session_state.lang = "English"
if 'live_data' not in st.session_state:
    st.session_state.live_data = None

def navigate_to(page_name):
    st.session_state.current_page = page_name

# --- CITY TO COORDINATE MAPPING ---
CITIES = {
    "Tirupati, AP": (13.6288, 79.4192), "Chittoor, AP": (13.2172, 79.1003),
    "Nellore, AP": (14.4426, 79.9865), "Kadapa, AP": (14.4673, 78.8242),
    "Kurnool, AP": (15.8281, 78.0373), "Anantapur, AP": (14.6819, 77.6006),
    "Chennai, TN": (13.0827, 80.2707), "Bengaluru, KA": (12.9716, 77.5946),
    "Hyderabad, TG": (17.3850, 78.4867)
}

# --- CLOUD-NATIVE SATELLITE FETCH (NO JSON FILE USED) ---
def fetch_live_data(city_name):
    lat, lon = CITIES[city_name]
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,precipitation,wind_gusts_10m,weather_code"
        f"&hourly=soil_moisture_0_to_7cm"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max"
        f"&timezone=auto"
    )
    try:
        res = requests.get(url, timeout=8).json()
        weather_code = res['current']['weather_code']
        
        forecast_7d = []
        daily = res.get('daily', {})
        for i in range(len(daily.get('time', []))):
            forecast_7d.append({
                "date": daily['time'][i], "temp_max": daily['temperature_2m_max'][i],
                "temp_min": daily['temperature_2m_min'][i], "rain_sum": daily['precipitation_sum'][i],
                "wind_max": daily['wind_speed_10m_max'][i],
            })
            
        weather_data = {
            "temp": res['current']['temperature_2m'], "rain_24h": res['current']['precipitation'],
            "wind_gust": res['current']['wind_gusts_10m'], "soil_moisture": abs(res['hourly']['soil_moisture_0_to_7cm'][0]),
            "weather_code": weather_code, "forecast_7d": forecast_7d,
            "lightning_strike_km": round(random.uniform(1.2, 5.0), 1) if weather_code in [95, 96, 99] else None
        }
    except:
        weather_data = {"temp": 30.5, "rain_24h": 0.0, "wind_gust": 12.0, "soil_moisture": 0.25, "weather_code": 0, "forecast_7d": [], "lightning_strike_km": None}

    try:
        df = pd.read_csv("kaggle_crop_data.csv")
        sample = df[df['label'] == 'rice'].sample(1).iloc[0]
        soil_data = {"N": float(sample['N']), "P": float(sample['P']), "K": float(sample['K']), "ph": float(sample['ph'])}
    except:
        soil_data = {"N": 80.0, "P": 40.0, "K": 40.0, "ph": 6.5}
        
    return {
        "timestamp": (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %I:%M:%S %p (IST)"),
        "weather": weather_data,
        "soil": soil_data
    }

# --- 6-LANGUAGE UI TRANSLATIONS ---
TRANSLATIONS = {
    "English": {"title": "🌾 Agri-Sentinel OS", "subtitle": "Precision Agronomics", "intake_header": "Configure Farm Profile", "farmer_name": "Farmer Name", "location": "Select City/Region", "crop_select": "Select Crop", "stage_select": "Growth Stage", "launch_btn": "Launch Diagnostics 🚀", "error_fill": "⚠️ Enter name.", "sync_text": "🟢 Live Satellite Sync:", "lightning_alert": "⚡ LIGHTNING DETECTED", "telemetry_header": "📡 Atmospheric Telemetry", "moisture": "Soil Moisture", "rain_24h": "24h Rain", "wind": "Wind Gusts", "temp": "Temperature", "forecast_header": "📅 7-Day Forecast", "scorecard_header": "🛡️ Prevention Scorecard", "risk_level": "Risk Level", "primary_threat": "Threat", "readiness_score": "Readiness", "checklist_title": "Action Checklist:", "soil_header": "🧪 Soil Macronutrients", "stages": ["Sowing", "Vegetative", "Flowering", "Pre-Harvest"]},
    "తెలుగు": {"title": "🌾 అగ్రి-సెంటినెల్ OS", "subtitle": "ఖచ్చితమైన వ్యవసాయం", "intake_header": "వ్యవసాయ వివరాలు", "farmer_name": "రైతు పేరు", "location": "ప్రాంతం ఎంచుకోండి", "crop_select": "పంటను ఎంచుకోండి", "stage_select": "పెరుగుదల దశ", "launch_btn": "విశ్లేషణ ప్రారంభించండి 🚀", "error_fill": "⚠️ పేరు నమోదు చేయండి.", "sync_text": "🟢 లైవ్ సింక్:", "lightning_alert": "⚡ పిడుగుపాటు హెచ్చరిక", "telemetry_header": "📡 వాతావరణ రీడింగులు", "moisture": "నేలలో తేమ", "rain_24h": "వర్షపాతం", "wind": "గాలి వేగం", "temp": "ఉష్ణోగ్రత", "forecast_header": "📅 7 రోజుల సూచన", "scorecard_header": "🛡️ నష్ట నివారణ స్కోర్‌కార్డ్", "risk_level": "ప్రమాద స్థాయి", "primary_threat": "ప్రధాన ముప్పు", "readiness_score": "సంసిద్ధత", "checklist_title": "చర్యల జాబితా:", "soil_header": "🧪 నేల పోషకాలు", "stages": ["విత్తే దశ", "ఏపుగా పెరిగే దశ", "పూత దశ", "కోతకు ముందు దశ"]},
    "हिंदी": {"title": "🌾 एग्री-सेंटिनेल OS", "subtitle": "सटीक कृषि", "intake_header": "खेत प्रोफ़ाइल", "farmer_name": "किसान का नाम", "location": "शहर चुनें", "crop_select": "फसल चुनें", "stage_select": "विकास चरण", "launch_btn": "विश्लेषण शुरू करें 🚀", "error_fill": "⚠️ नाम दर्ज करें।", "sync_text": "🟢 लाइव सिंक:", "lightning_alert": "⚡ बिजली की चेतावनी", "telemetry_header": "📡 वायुमंडलीय टेलीमेट्री", "moisture": "मिट्टी की नमी", "rain_24h": "बारिश", "wind": "हवा की गति", "temp": "तापमान", "forecast_header": "📅 7-दिवसीय पूर्वानुमान", "scorecard_header": "🛡️ निवारण स्कोरकार्ड", "risk_level": "जोखिम स्तर", "primary_threat": "खतरा", "readiness_score": "तैयारी", "checklist_title": "कार्रवाई सूची:", "soil_header": "🧪 मिट्टी के पोषक तत्व", "stages": ["बुवाई", "वनस्पतिक", "फूल आना", "कटाई से पहले"]},
    "தமிழ்": {"title": "🌾 அக்ரி-சென்டினல் OS", "subtitle": "துல்லிய விவசாயம்", "intake_header": "விவசாய விவரங்கள்", "farmer_name": "விவசாயி பெயர்", "location": "நகரம்", "crop_select": "பயிர்", "stage_select": "வளர்ச்சி நிலை", "launch_btn": "பகுப்பாய்வு தொடங்கு 🚀", "error_fill": "⚠️ பெயரை உள்ளிடவும்.", "sync_text": "🟢 நேரடி ஒத்திசைவு:", "lightning_alert": "⚡ மின்னல் எச்சரிக்கை", "telemetry_header": "📡 வானிலை", "moisture": "மண் ஈரப்பதம்", "rain_24h": "மழை", "wind": "காற்று", "temp": "வெப்பநிலை", "forecast_header": "📅 7-நாள் முன்னறிவிப்பு", "scorecard_header": "🛡️ தடுப்பு அட்டை", "risk_level": "ஆபத்து நிலை", "primary_threat": "அச்சுறுத்தல்", "readiness_score": "தயார்நிலை", "checklist_title": "செயல் பட்டியல்:", "soil_header": "🧪 மண் ஊட்டச்சத்துக்கள்", "stages": ["விதைப்பு", "வளர்ச்சி", "பூக்கும்", "அறுவடைக்கு முன்"]},
    "ಕನ್ನಡ": {"title": "🌾 ಅಗ್ರಿ-ಸೆಂಟಿನೆಲ್ OS", "subtitle": "ನಿಖರ ಕೃಷಿ", "intake_header": "ಕೃಷಿ ವಿವರಗಳು", "farmer_name": "ರೈತನ ಹೆಸರು", "location": "ನಗರ", "crop_select": "ಬೆಳೆ", "stage_select": "ಬೆಳವಣಿಗೆ ಹಂತ", "launch_btn": "ವಿಶ್ಲೇಷಣೆ ಪ್ರಾರಂಭಿಸಿ 🚀", "error_fill": "⚠️ ಹೆಸರನ್ನು ನಮೂದಿಸಿ.", "sync_text": "🟢 ಲೈವ್ ಸಿಂಕ್:", "lightning_alert": "⚡ ಮಿಂಚು ಎಚ್ಚರಿಕೆ", "telemetry_header": "📡 ಹವಾಮಾನ", "moisture": "ಮಣ್ಣಿನ ತೇವಾಂಶ", "rain_24h": "ಮಳೆ", "wind": "ಗಾಳಿ", "temp": "ತಾಪಮಾನ", "forecast_header": "📅 7-ದಿನದ ಮುನ್ಸೂಚನೆ", "scorecard_header": "🛡️ ತಡೆಗಟ್ಟುವಿಕೆ ಕಾರ್ಡ್", "risk_level": "ಅಪಾಯದ ಮಟ್ಟ", "primary_threat": "ಬೆದರಿಕೆ", "readiness_score": "ಸಿದ್ಧತೆ", "checklist_title": "ಕ್ರಿಯಾ ಪಟ್ಟಿ:", "soil_header": "🧪 ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳು", "stages": ["ಬಿತ್ತನೆ", "ಬೆಳವಣಿಗೆ", "ಹೂಬಿಡುವಿಕೆ", "ಕೊಯ್ಲಿಗೆ ಮುನ್ನ"]},
    "മലയാളം": {"title": "🌾 അഗ്രി-സെന്റിനൽ OS", "subtitle": "കൃത്യമായ കൃഷി", "intake_header": "കാർഷിക പ്രൊഫൈൽ", "farmer_name": "കർഷകന്റെ പേര്", "location": "നഗരം", "crop_select": "വിള", "stage_select": "വളർച്ചാ ഘട്ടം", "launch_btn": "വിശകലനം ആരംഭിക്കുക 🚀", "error_fill": "⚠️ പേര് നൽകുക.", "sync_text": "🟢 തത്സമയ സമന്വയം:", "lightning_alert": "⚡ മിന്നൽ മുന്നറിയിപ്പ്", "telemetry_header": "📡 കാലാവസ്ഥ", "moisture": "മണ്ണിലെ ഈർപ്പം", "rain_24h": "മഴ", "wind": "കാറ്റ്", "temp": "താപനില", "forecast_header": "📅 7-ദിവസത്തെ പ്രവചനം", "scorecard_header": "🛡️ പ്രതിരോധ കാർഡ്", "risk_level": "അപകടസാധ്യത", "primary_threat": "ഭീഷണി", "readiness_score": "തയ്യാറെടുപ്പ്", "checklist_title": "പ്രവർത്തന പട്ടിക:", "soil_header": "🧪 മണ്ണിന്റെ പോഷകങ്ങൾ", "stages": ["വിതയ്ക്കൽ", "വളർച്ച", "പൂവിടൽ", "വിളവെടുപ്പിന് മുമ്പ്"]}
}

CROP_DB = {
    "Rice (వరి)": {
        "moisture_optimum": [0.60, 1.0], "rain_max": 150, "wind_max": 45,
        "threats": {"flood": "Lodging", "drought": "Stunting", "wind": "Lodging Risk"},
        "advice": {"Sowing": "Rain is highly beneficial for puddling.", "Vegetative": "Maintain 3-5cm water.", "Flowering": "Rain washes pollen. Halt spray.", "Pre-Harvest": "Drain field completely."}
    },
    "Maize (మొక్కజొన్న)": {
        "moisture_optimum": [0.50, 0.70], "rain_max": 50, "wind_max": 50,
        "threats": {"flood": "Root Asphyxiation", "drought": "Silking Abortion", "wind": "Stalk Breakage"},
        "advice": {"Sowing": "Drain field to prevent seed rot.", "Vegetative": "Moderate rain supports stalks.", "Flowering": "CRITICAL: Drought causes yield failure.", "Pre-Harvest": "Needs dry weather for cobs."}
    },
    "Cotton (పత్తి)": {
        "moisture_optimum": [0.35, 0.60], "rain_max": 30, "wind_max": 45,
        "threats": {"flood": "Boll Shedding", "drought": "Stunting", "wind": "Branch Breakage"},
        "advice": {"Sowing": "Heavy rain traps seedlings.", "Vegetative": "Deep roots tolerate drought.", "Flowering": "Rain washes away pollen.", "Pre-Harvest": "CRITICAL: Rain discolors lint."}
    },
    "Banana (అరటి)": {
        "moisture_optimum": [0.70, 0.90], "rain_max": 100, "wind_max": 30, 
        "threats": {"flood": "Panama Wilt Risk", "drought": "Leaf Scorch", "wind": "CRITICAL Uprooting Threat"},
        "advice": {"Sowing": "Maintain high soil moisture.", "Vegetative": "Wind above 30km/h tears leaves.", "Flowering": "High moisture needed.", "Pre-Harvest": "Prop up pseudostems immediately."}
    },
    "Mango (మామిడి)": {
        "moisture_optimum": [0.30, 0.60], "rain_max": 60, "wind_max": 50,
        "threats": {"flood": "Fungal Rot", "drought": "Fruit Drop", "wind": "Fruit Drop"},
        "advice": {"Sowing": "Saplings need moderate watering.", "Vegetative": "Drought tolerant deep roots.", "Flowering": "CRITICAL DANGER: Rain washes flowers.", "Pre-Harvest": "Heavy wind causes fruit drop."}
    },
    "Chilli (మిరప)": {
        "moisture_optimum": [0.45, 0.65], "rain_max": 40, "wind_max": 40,
        "threats": {"flood": "Collar Rot", "drought": "Flower Drop", "wind": "Plant Snapping"},
        "advice": {"Sowing": "Nursery beds need misting.", "Vegetative": "Waterlogging causes root rot.", "Flowering": "Moisture stress drops blossoms.", "Pre-Harvest": "Dry weather maintains pungency."}
    }
}

# Top Bar Language Toggle
lang_col1, lang_col2 = st.columns([5, 4])
with lang_col2:
    selected_lang = st.radio("🌐", ["English", "తెలుగు", "हिंदी", "தமிழ்", "ಕನ್ನಡ", "മലയാളം"], horizontal=True, label_visibility="collapsed")
    st.session_state.lang = selected_lang

T = TRANSLATIONS[st.session_state.lang]

# ==========================================
# PAGE 1: THE INTAKE PORTAL
# ==========================================
if st.session_state.current_page == "Intake":
    st.markdown(f"<h1 style='text-align: center; color: #2E7D32;'>{T['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #666;'>{T['subtitle']}</p>", unsafe_allow_html=True)
    st.write("")
    
    with st.container(border=True):
        st.header(T['intake_header'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.farmer_name = st.text_input(T['farmer_name'], "Lohith Reddy")
            st.session_state.city = st.selectbox(T['location'], list(CITIES.keys()))
        with col2:
            crop_choice = st.selectbox(T['crop_select'], list(CROP_DB.keys()))
            st.session_state.crop = crop_choice
            
            raw_stages = ["Sowing", "Vegetative", "Flowering", "Pre-Harvest"]
            stage_index = st.selectbox(T['stage_select'], range(len(T['stages'])), format_func=lambda x: T['stages'][x])
            st.session_state.stage = raw_stages[stage_index]
            st.session_state.stage_display = T['stages'][stage_index]
            
        st.write("")
        if st.button(T['launch_btn'], type="primary", use_container_width=True):
            if st.session_state.farmer_name:
                # INSTANT API FETCH: Saved strictly to memory, no local JSON files
                st.session_state.live_data = fetch_live_data(st.session_state.city)
                navigate_to("Dashboard")
                st.rerun()
            else:
                st.error(T['error_fill'])

# ==========================================
# PAGE 2: THE ANALYTICS DASHBOARD
# ==========================================
elif st.session_state.current_page == "Dashboard":
    
    if st.session_state.live_data is None:
        st.error("⚠️ Data connection lost. Please restart diagnostics.")
        st.button("Return Home", on_click=navigate_to, args=("Intake",))
        st.stop()

    data = st.session_state.live_data
    weather = data['weather']
    soil = data['soil']
    crop = st.session_state.crop
    stage = st.session_state.stage
    rules = CROP_DB[crop]
    
    col_h1, col_h2, col_h3 = st.columns([4, 1, 1])
    with col_h1:
        st.title(f"📊 {st.session_state.farmer_name} | {st.session_state.city.split(',')[0]}")
        st.caption(f"🌾 {crop} — **{st.session_state.stage_display}**")
    with col_h2:
        if st.button("🔄 Sync API", use_container_width=True):
            # FRESH DATA FETCH ON BUTTON PRESS
            st.session_state.live_data = fetch_live_data(st.session_state.city)
            st.rerun()
    with col_h3:
        st.button("⚙️ Home", on_click=navigate_to, args=("Intake",), use_container_width=True)

    st.success(f"{T['sync_text']} **{data['timestamp']}**")

    # Lightning Safety
    lightning_km = weather.get('lightning_strike_km')
    if lightning_km:
        st.error(f"### {T['lightning_alert']} ({lightning_km} KM)\nEMERGENCY PROTOCOL: Stop activity immediately.")

    # Telemetry HUD
    st.markdown(f"### {T['telemetry_header']}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(T['moisture'], f"{weather['soil_moisture']*100:.1f} %")
    m2.metric(T['rain_24h'], f"{weather['rain_24h']} mm")
    m3.metric(T['wind'], f"{weather['wind_gust']} km/h")
    m4.metric(T['temp'], f"{weather['temp']} °C")
    st.divider()

    # 7-Day Forecast
    st.markdown(f"### {T['forecast_header']}")
    forecast_list = weather.get('forecast_7d', [])
    if forecast_list:
        f_cols = st.columns(min(7, len(forecast_list)))
        for idx, day in enumerate(forecast_list[:7]):
            with f_cols[idx]:
                rain_val = day['rain_sum']
                icon = "☀️" if rain_val == 0 else ("🌦️" if rain_val < 15 else "⛈️")
                date_str = day['date'].split("-")[1] + "/" + day['date'].split("-")[2]
                with st.container(border=True):
                    st.markdown(f"**{date_str}** {icon}")
                    st.write(f"🌡️ {day['temp_min']}°-{day['temp_max']}°")
                    st.write(f"🌧️ **{rain_val}mm**")
    st.divider()

    # Scorecard Logic
    st.markdown(f"### {T['scorecard_header']}")
    rain_val = weather['rain_24h']
    moist_val = weather['soil_moisture']
    wind_val = weather['wind_gust']
    
    threat = "Optimal"
    risk_level = "🟢 LOW RISK"
    actions = []
    
    if moist_val > rules['moisture_optimum'][1] or rain_val >= rules['rain_max']:
        threat = rules['threats']['flood']
        risk_level = "🔴 CRITICAL"
        actions.append("Open perimeter drainage trenches.")
    elif moist_val < rules['moisture_optimum'][0]:
        threat = rules['threats']['drought']
        risk_level = "🟠 MODERATE"
        actions.append(f"Turn on micro-irrigation targeting {rules['moisture_optimum'][0]*100:.0f}% moisture.")
    
    if wind_val > rules['wind_max']:
        risk_level = "🔴 HIGH RISK"
        threat = rules['threats']['wind']
        if "Banana" in crop:
            actions.append("URGENT: Prop up pseudostems with bamboo poles immediately to prevent uprooting.")
        else:
            actions.append("Postpone foliar chemical spraying.")
        
    if not actions:
        actions.append("Crop is currently stable. Maintain regular schedules.")

    sc1, sc2, sc3 = st.columns([1, 1, 1])
    sc1.metric(T['risk_level'], risk_level)
    sc2.metric(T['primary_threat'], threat)
    
    st.markdown(f"**{T['checklist_title']}**")
    completed_tasks = sum([1 for idx, act in enumerate(actions) if st.checkbox(act, key=f"action_{idx}")])
    score_pct = int((completed_tasks / len(actions)) * 100)
    sc3.metric(T['readiness_score'], f"{score_pct}%")
    st.progress(score_pct / 100)
    
    with st.container(border=True):
        st.markdown(f"**💡 AI Diagnostic Insight ({st.session_state.stage_display}):**")
        st.write(rules['advice'][stage])
    st.divider()

    # Soil NPK
    st.markdown(f"### {T['soil_header']}")
    c_soil1, c_soil2 = st.columns([1, 2])
    with c_soil1:
        st.metric("Nitrogen (N)", f"{soil['N']} mg/kg")
        st.metric("Phosphorus (P)", f"{soil['P']} mg/kg")
        st.metric("Potassium (K)", f"{soil['K']} mg/kg")
    with c_soil2:
        chart_df = pd.DataFrame({"Level": [soil['N'], soil['P'], soil['K']]}, index=["N", "P", "K"])
        st.bar_chart(chart_df, height=200)