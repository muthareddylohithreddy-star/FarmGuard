import streamlit as st
import pandas as pd
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Agri-Sentinel OS", page_icon="🌾", layout="wide", initial_sidebar_state="collapsed")

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Intake"
if 'lang' not in st.session_state:
    st.session_state.lang = "English"

def navigate_to(page_name):
    st.session_state.current_page = page_name

# --- BILINGUAL UI TRANSLATIONS (ENGLISH / తెలుగు) ---
TRANSLATIONS = {
    "English": {
        "title": "🌾 Agri-Sentinel Operating System",
        "subtitle": "Precision Agronomics & Real-Time Disaster Intelligence",
        "intake_header": "1. Configure Farm Profile",
        "farmer_name": "Farmer / Plot Owner Name",
        "location": "Location (City/Mandal)",
        "crop_select": "Select Target Crop",
        "stage_select": "Current Growth Stage",
        "launch_btn": "Launch Deep Diagnostics 🚀",
        "error_fill": "⚠️ Please enter the Farmer Name and Location before proceeding.",
        "reconfig_btn": "⚙️ Reconfigure",
        "sync_text": "🟢 Synchronized with Edge Node. Last packet:",
        "lightning_alert": "⚡ TACTICAL ALERT: LIGHTNING STRIKE DETECTED",
        "lightning_advice": "EMERGENCY PROTOCOL: Stop all agricultural activity immediately. Ground metal equipment (tractors, tillers). Do NOT seek shelter under isolated trees. Move to a concrete building or enclosed vehicle.",
        "telemetry_header": "📡 Live Atmospheric & Sensor Telemetry",
        "moisture": "Volumetric Soil Moisture",
        "rain_24h": "24h Rain Accumulation",
        "wind": "Wind Gusts",
        "temp": "Ambient Temperature",
        "forecast_header": "📅 7-Day Live Forecast & Advance Alerts",
        "adv_badge": "⚠️ ADVANCE ALERT",
        "scorecard_header": "🛡️ Crop Loss Prevention Scorecard",
        "risk_level": "Assessed Risk Level",
        "primary_threat": "Primary Threat",
        "readiness_score": "Farm Mitigation Readiness",
        "checklist_title": "Field Action Checklist (Check once completed):",
        "soil_header": "🧪 Live Soil Macronutrients (N-P-K)",
        "sos_header": "🆘 Emergency Support & Farmer Helplines",
        "opt_moisture": "Optimal Soil Moisture",
        "stages": ["Sowing", "Vegetative", "Flowering", "Pre-Harvest"]
    },
    "తెలుగు": {
        "title": "🌾 అగ్రి-సెంటినెల్ ఆపరేటింగ్ సిస్టమ్",
        "subtitle": "ఖచ్చితమైన వ్యవసాయ విశ్లేషణ & విపత్తు హెచ్చరిక వ్యవస్థ",
        "intake_header": "1. వ్యవసాయ వివరాలను నమోదు చేయండి",
        "farmer_name": "రైతు పేరు",
        "location": "ప్రాంతం (నగరం / మండలం)",
        "crop_select": "పంటను ఎంచుకోండి",
        "stage_select": "ప్రస్తుత పెరుగుదల దశ",
        "launch_btn": "సమగ్ర విశ్లేషణను ప్రారంభించండి 🚀",
        "error_fill": "⚠️ దయచేసి ముందుకు వెళ్ళేముందు రైతు పేరు మరియు ప్రాంతాన్ని నమోదు చేయండి.",
        "reconfig_btn": "⚙️ వివరాలు మార్చండి",
        "sync_text": "🟢 సెన్సార్ డేటాతో అనుసంధానించబడింది. తాజా అప్‌డేట్:",
        "lightning_alert": "⚡ అత్యవసర హెచ్చరిక: సమీపంలో పిడుగుపాటు గుర్తించబడింది",
        "lightning_advice": "రక్షణ చర్య: వ్యవసాయ పనులను తక్షణమే నిలిపివేయండి. ట్రాక్టర్లు మరియు లోహపు పరికరాలకు దూరంగా ఉండండి. ఒంటరి చెట్ల క్రింద నిలబడవద్దు. వెంటనే సురక్షితమైన భవనంలోకి వెళ్ళండి.",
        "telemetry_header": "📡 ప్రత్యక్ష వాతావరణ & సెన్సార్ రీడింగులు",
        "moisture": "నేలలో తేమ శాతం",
        "rain_24h": "24 గంటల వర్షపాతం",
        "wind": "గాలి వేగం",
        "temp": "ఉష్ణోగ్రత",
        "forecast_header": "📅 7 రోజుల వాతావరణ సూచన & ముందస్తు హెచ్చరికలు",
        "adv_badge": "⚠️ ముందస్తు హెచ్చరిక",
        "scorecard_header": "🛡️ పంట నష్ట నివారణ స్కోర్‌కార్డ్ (Risk Scorecard)",
        "risk_level": "ప్రమాద తీవ్రత స్థాయి",
        "primary_threat": "ప్రధాన ముప్పు",
        "readiness_score": "రైతు సంసిద్ధత స్కోరు",
        "checklist_title": "క్షేత్రస్థాయి చర్యల చెక్‌లిస్ట్ (పూర్తయిన వాటిని టిక్ చేయండి):",
        "soil_header": "🧪 నేల పోషకాల విశ్లేషణ (N-P-K)",
        "sos_header": "🆘 అత్యవసర ప్రభుత్వ సహాయ నంబర్లు",
        "opt_moisture": "అనుకూలమైన తేమ స్థాయి",
        "stages": ["విత్తే దశ (Sowing)", "ఏపుగా పెరిగే దశ (Vegetative)", "పూత దశ (Flowering)", "కోతకు ముందు దశ (Pre-Harvest)"]
    }
}

# --- EXTENDED CROP KNOWLEDGE BASE ---
CROP_DB = {
    "Rice (వరి)": {
        "moisture_optimum": [0.60, 1.0], "rain_max": 150,
        "threats": {"flood": "Waterlogging & Lodging", "drought": "Severe Tillering Stunt", "safe": "Conditions Optimal"},
        "advice_en": {
            "Sowing": "Rain is beneficial. Keeps puddle water ready for transplanting.",
            "Vegetative": "Maintain 3-5cm standing water. Current conditions support tillering.",
            "Flowering": "Heavy rain and gusts wash off pollen. Halt chemical spraying.",
            "Pre-Harvest": "DANGER: Drain field completely 15 days before harvest. Rain causes grain shattering."
        },
        "advice_te": {
            "Sowing": "వర్షం ఎంతో మేలు చేస్తుంది. నాట్లు వేయడానికి అనుకూలం.",
            "Vegetative": "మడిలో 3-5 సెం.మీ నీరు ఉంచండి. ఈ వాతావరణం పిలకలు వేయడానికి సహాయపడుతుంది.",
            "Flowering": "భారీ వర్షం పడితే పుప్పొడి కొట్టుకుపోతుంది. పురుగుమందుల పిచికారీ నిలిపివేయండి.",
            "Pre-Harvest": "ప్రమాదం: కోతకు 15 రోజుల ముందు పొలంలో నీటిని తీసివేయాలి. వర్షం పడితే గింజ రాలిపోతుంది."
        }
    },
    "Wheat (గోధుమ)": {
        "moisture_optimum": [0.40, 0.65], "rain_max": 40,
        "threats": {"flood": "Root Rot & Fungal Rust", "drought": "Tillering Failure", "safe": "Conditions Optimal"},
        "advice_en": {
            "Sowing": "Requires moderate soil moisture for seedling emergence. Avoid heavy water.",
            "Vegetative": "Crown root stage requires moisture. Light rain reduces irrigation needs.",
            "Flowering": "Rain now causes rust and earhead mold.",
            "Pre-Harvest": "DANGER: Wind and rain now cause crop lodging and mold development."
        },
        "advice_te": {
            "Sowing": "మొలక రావడానికి తగినంత తేమ అవసరం. పొలంలో నీరు నిలవనీయవద్దు.",
            "Vegetative": "వేరు వ్యవస్థ బలపడే సమయం. తేలికపాటి వర్షం ఉపయోగకరం.",
            "Flowering": "ఈ సమయంలో వర్షం పడితే తెగుళ్లు, బూజు వచ్చే ప్రమాదం ఉంది.",
            "Pre-Harvest": "ప్రమాదం: బలమైన ఈదురుగాలులు పంట నేలకూలేలా చేస్తాయి."
        }
    },
    "Maize (మొక్కజొన్న)": {
        "moisture_optimum": [0.50, 0.70], "rain_max": 50,
        "threats": {"flood": "Root Asphyxiation in 24h", "drought": "Silking Abortion", "safe": "Conditions Optimal"},
        "advice_en": {
            "Sowing": "Needs warm, well-aerated soil. Standing water rots seeds.",
            "Vegetative": "Rapid vegetative growth. Rain supports strong stalk development.",
            "Flowering": "CRITICAL: Silking and tasseling stage. Moisture stress causes barren cobs.",
            "Pre-Harvest": "Needs dry weather for cob hardening. Rain causes aflatoxin fungal infection."
        },
        "advice_te": {
            "Sowing": "విత్తనాలు కుళ్ళిపోకుండా నేలలో నీరు నిల్వ ఉండకుండా చూడండి.",
            "Vegetative": "మొక్క ఏపుగా పెరిగే దశ. వర్షం కాండం బలానికి సహాయపడుతుంది.",
            "Flowering": "చాలా ముఖ్యమైన దశ (కంకి పట్టే సమయం). నీటి ఎద్దడి లేకుండా చూడండి.",
            "Pre-Harvest": "కంకి ఎండటానికి పొడి వాతావరణం అవసరం. వర్షం వల్ల బూజు పడుతుంది."
        }
    },
    "Cotton (పత్తి)": {
        "moisture_optimum": [0.35, 0.60], "rain_max": 30,
        "threats": {"flood": "Boll Shedding & Rot", "drought": "Premature Stunting", "safe": "Conditions Optimal"},
        "advice_en": {
            "Sowing": "Requires warm soil. Heavy rainfall compacts soil and traps seedlings.",
            "Vegetative": "Deep taproot enables moderate drought tolerance.",
            "Flowering": "DANGER: Rain drops floral buds (squares) and washes away pollen.",
            "Pre-Harvest": "CRITICAL DANGER: Rain on open cotton bolls discolors lint and causes boll rot."
        },
        "advice_te": {
            "Sowing": "విత్తనం నాటిన వెంటనే భారీ వర్షం పడితే మొలక శాతం తగ్గుతుంది.",
            "Vegetative": "లోతైన వేరు వ్యవస్థ వల్ల సాధారణ బెట్టను తట్టుకుంటుంది.",
            "Flowering": "ప్రమాదం: వర్షం పడితే పూత, పిందె రాలిపోతాయి.",
            "Pre-Harvest": "తీవ్ర ప్రమాదం: పగిలిన కాయలపై వర్షం పడితే దూది నాణ్యత దెబ్బతింటుంది, కాయ కుళ్ళు వస్తుంది."
        }
    },
    "Tomato (టమాటా)": {
        "moisture_optimum": [0.55, 0.75], "rain_max": 25,
        "threats": {"flood": "Early/Late Blight & Fruit Cracking", "drought": "Blossom End Rot", "safe": "Conditions Optimal"},
        "advice_en": {
            "Sowing": "Nursery beds need gentle misting. Heavy rain destroys young seedlings.",
            "Vegetative": "High humidity triggers immediate early blight. Ensure ridge drainage.",
            "Flowering": "Rain washes off blooms. Keep irrigation strictly at ground level.",
            "Pre-Harvest": "Sudden heavy rain after a dry spell causes immediate fruit skin cracking."
        },
        "advice_te": {
            "Sowing": "నారుమడిలో నీరు నిలవకుండా చూడండి. భారీ వర్షం నారును పాడుచేస్తుంది.",
            "Vegetative": "గాలిలో అధిక తేమ వల్ల ఆకుమచ్చ తెగులు వ్యాపిస్తుంది. బోదెలు శుభ్రం చేయండి.",
            "Flowering": "వర్షపు చినుకులు పూత రాలడానికి కారణమవుతాయి.",
            "Pre-Harvest": "ఎండ తర్వాత హఠాత్తుగా భారీ వర్షం పడితే కాయలు పగులుతాయి."
        }
    }
}

def load_live_data():
    try:
        with open("live_farm_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# Top Bar Language Toggle
lang_col1, lang_col2 = st.columns([6, 1])
with lang_col2:
    selected_lang = st.radio("🌐 Language / భాష", ["English", "తెలుగు"], horizontal=True, label_visibility="collapsed")
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
            st.session_state.city = st.text_input(T['location'], "Tirupati")
        with col2:
            crop_choice = st.selectbox(T['crop_select'], list(CROP_DB.keys()))
            st.session_state.crop = crop_choice
            
            raw_stages = ["Sowing", "Vegetative", "Flowering", "Pre-Harvest"]
            stage_index = st.selectbox(T['stage_select'], range(len(T['stages'])), format_func=lambda x: T['stages'][x])
            st.session_state.stage = raw_stages[stage_index]
            st.session_state.stage_display = T['stages'][stage_index]
            
        st.write("")
        if st.button(T['launch_btn'], type="primary", use_container_width=True):
            if st.session_state.farmer_name and st.session_state.city:
                navigate_to("Dashboard")
                st.rerun()
            else:
                st.error(T['error_fill'])

# ==========================================
# PAGE 2: THE ANALYTICS DASHBOARD
# ==========================================
elif st.session_state.current_page == "Dashboard":
    
    data = load_live_data()
    if not data:
        st.error("⚠️ Background Edge Node Offline. Please run 'python edge_node.py' in your terminal.")
        st.button("Back to Configuration", on_click=navigate_to, args=("Intake",))
        st.stop()

    weather = data['weather']
    soil = data['soil']
    crop = st.session_state.crop
    stage = st.session_state.stage
    rules = CROP_DB[crop]
    
    # Header & Reconfigure button
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        st.title(f"📊 {st.session_state.farmer_name} | {st.session_state.city}")
        st.caption(f"🌾 {crop} — **{st.session_state.stage_display}**")
    with col_h2:
        st.button(T['reconfig_btn'], on_click=navigate_to, args=("Intake",), use_container_width=True)

    st.success(f"{T['sync_text']} **{data['timestamp']}**")

    # --- 1. LIGHTNING LIFE SAFETY OVERRIDE ---
    lightning_km = weather.get('lightning_strike_km')
    if lightning_km:
        st.error(f"### {T['lightning_alert']} ({lightning_km} KM)\n**{T['lightning_advice']}**")

    # --- 2. LIVE TELEMETRY HUD ---
    st.markdown(f"### {T['telemetry_header']}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(T['moisture'], f"{weather['soil_moisture']*100:.1f} %")
    m2.metric(T['rain_24h'], f"{weather['rain_24h']} mm")
    m3.metric(T['wind'], f"{weather['wind_gust']} km/h")
    m4.metric(T['temp'], f"{weather['temp']} °C")
    st.divider()

    # --- 3. 7-DAY FORECAST & ADVANCE WARNINGS ---
    st.markdown(f"### {T['forecast_header']}")
    
    # Advance Alert Banner if detected
    adv_warning = weather.get('advance_warning')
    if adv_warning:
        st.warning(f"**{T['adv_badge']}:** {adv_warning}")
    
    forecast_list = weather.get('forecast_7d', [])
    if forecast_list:
        f_cols = st.columns(min(7, len(forecast_list)))
        for idx, day in enumerate(forecast_list[:7]):
            with f_cols[idx]:
                # Visual badge based on rain
                rain_val = day['rain_sum']
                icon = "☀️" if rain_val == 0 else ("🌦️" if rain_val < 15 else "⛈️")
                date_str = day['date'].split("-")[1] + "/" + day['date'].split("-")[2] # MM/DD
                
                with st.container(border=True):
                    st.markdown(f"**{date_str}** {icon}")
                    st.write(f"🌡️ {day['temp_min']}°-{day['temp_max']}°")
                    st.write(f"🌧️ **{rain_val} mm**")
                    st.caption(f"💨 {day['wind_max']} km/h")
    st.divider()

    # --- 4. CROP LOSS PREVENTION SCORECARD ---
    st.markdown(f"### {T['scorecard_header']}")
    
    # Calculate Risk & Threats
    rain_val = weather['rain_24h']
    moist_val = weather['soil_moisture']
    wind_val = weather['wind_gust']
    
    threat = "Optimal"
    risk_level = "🟢 LOW RISK"
    actions = []
    
    # Evaluate risks against crop rules
    if moist_val > rules['moisture_optimum'][1] or rain_val >= rules['rain_max']:
        threat = rules['threats']['flood']
        risk_level = "🔴 CRITICAL (FLOOD/ROOT ROT)"
        actions.append("Open perimeter drainage trenches to evacuate excess water.")
        actions.append("Halt all urea and water-soluble fertilizer applications to avoid runoff.")
    elif moist_val < rules['moisture_optimum'][0]:
        threat = rules['threats']['drought']
        risk_level = "🟠 MODERATE (MOISTURE STRESS)"
        actions.append(f"Turn on micro-irrigation targeting {rules['moisture_optimum'][0]*100:.0f}% moisture.")
    
    if wind_val > 40 and stage in ["Flowering", "Pre-Harvest"]:
        risk_level = "🔴 HIGH (WIND LODGING)"
        threat += " + Gale Lodging Risk"
        actions.append("Postpone all foliar chemical spraying (prevent spray drift loss).")
        
    if not actions:
        actions.append("Crop is currently stable. Maintain regular scouting and watering schedules.")
        actions.append("Check soil moisture again in 12 hours.")

    # Scorecard Metrics
    sc1, sc2, sc3 = st.columns([1, 1, 1])
    sc1.metric(T['risk_level'], risk_level)
    sc2.metric(T['primary_threat'], threat)
    
    # Interactive checklist for judges to interact with
    st.markdown(f"**{T['checklist_title']}**")
    completed_tasks = 0
    for idx, act in enumerate(actions):
        chk = st.checkbox(act, key=f"action_{idx}")
        if chk:
            completed_tasks += 1
            
    # Calculate Dynamic Mitigation Score
    score_pct = int((completed_tasks / len(actions)) * 100)
    sc3.metric(T['readiness_score'], f"{score_pct}%", delta="Protected" if score_pct == 100 else "Pending Action")
    st.progress(score_pct / 100)
    
    # Detailed Agronomic Explanation in Selected Language
    advice_text = rules['advice_te'][stage] if st.session_state.lang == "తెలుగు" else rules['advice_en'][stage]
    with st.container(border=True):
        st.markdown(f"**💡 Agronomic Diagnostic Summary ({crop} - {st.session_state.stage_display}):**")
        st.write(advice_text)
    st.divider()

    # --- 5. SOIL MACRONUTRIENT BARS (N-P-K) ---
    st.markdown(f"### {T['soil_header']}")
    c_soil1, c_soil2 = st.columns([1, 2])
    with c_soil1:
        st.metric("Nitrogen (N)", f"{soil['N']} mg/kg")
        st.metric("Phosphorus (P)", f"{soil['P']} mg/kg")
        st.metric("Potassium (K)", f"{soil['K']} mg/kg")
        st.metric("Soil pH Level", f"{soil['ph']:.2f}")
    with c_soil2:
        chart_df = pd.DataFrame(
            {"Level (mg/kg)": [soil['N'], soil['P'], soil['K']]}, 
            index=["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"]
        )
        st.bar_chart(chart_df, height=280)
    st.divider()

    # --- 6. EMERGENCY HELPLINES DIRECTORY ---
    st.markdown(f"### {T['sos_header']}")
    sos1, sos2, sos3, sos4 = st.columns(4)
    with sos1:
        st.error("**🚑 Medical Emergency**\n\nCall **108** / **112** (Ambulance, Snakebite support)")
    with sos2:
        st.warning("**🌾 Kisan Call Centre**\n\nCall **1800-180-1551** (Free Agri Expert Advice)")
    with sos3:
        st.info("**🚒 Fire & Disaster**\n\nCall **101** (Emergency Rescue & Fire Services)")
    with sos4:
        st.success("**📞 AP Rythu Bharosa**\n\nCall **155251** (State Farmer Grievance & Relief)")