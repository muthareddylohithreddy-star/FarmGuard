# 🌾 Agri-Sentinel OS (FarmGuard)

**Precision Agronomics & Real-Time Disaster Intelligence via Decoupled Edge-Computing**

Agri-Sentinel OS is a complete, decoupled Edge-IoT ecosystem designed to protect farmers from sudden weather shifts and agronomic threats. Moving beyond reactive, traditional weather applications, this project features a 24/7 background hardware simulator that actively pushes life-safety alerts to a farmer's device via `ntfy.sh`, paired with an interactive, 6-language analytical dashboard[cite: 2, 3].

---

## 🏗️ System Architecture

To guarantee high fault tolerance and continuous monitoring, the system is separated into three distinct layers:

### 1. The Edge Daemon (`edgenode.py`)
Operating as the "hardware brain" (simulating an ESP32/Raspberry Pi field node), this Python script runs continuously in the background[cite: 2]. 
* **Live Telemetry:** Connects to the Open-Meteo satellite API to fetch real-time atmospheric data (temperature, wind gusts, rainfall, and WMO weather codes)[cite: 2].
* **Active Disaster Logic:** Scans for WMO Thunderstorm Codes (95, 96, 99) and extreme weather thresholds[cite: 2]. 
* **Automated Push Notifications:** When a life-safety threshold is breached, it independently dispatches an HTTP POST request to the `ntfy.sh` server, pushing an emergency alert directly to the farmer's phone without requiring an active browser[cite: 2]. It includes a 60-second cooldown cycle to prevent alert fatigue and network rate-limiting[cite: 2].
* **Network Fault Tolerance:** Features a built-in `try/except` fallback loop; if the local Wi-Fi drops, it seamlessly generates simulated fallback data to keep the hardware running[cite: 2].

### 2. The Data Bridge (`live_farm_data.json`)
Since the front and back ends are decoupled, they communicate via a local JSON state manager[cite: 2, 4]. The edge node constantly overwrites this file with the latest timestamped telemetry and soil N-P-K data, acting as a lightweight, real-time database[cite: 2, 4].

### 3. The Central Dashboard (`farmguardapp_04.py`)
A Streamlit-based web application that visually translates the raw hardware data into actionable agronomic intelligence[cite: 3].
* **On-Demand API Override:** Features a "Force Sync" capability allowing users to select from 9 different South Indian cities (e.g., Tirupati, Bengaluru, Chennai) and instantly ping the Open-Meteo satellite for localized data, overriding the local JSON database[cite: 3].
* **AI Crop Prevention Scorecard:** Contains deep agronomic logic for 6 specific crops (Rice, Maize, Cotton, Banana, Mango, Chilli)[cite: 3]. For example, the system knows that Banana crops face critical uprooting threats at wind speeds of >30 km/h and dynamically updates the mitigation checklist accordingly[cite: 3].
* **Universal Accessibility:** A built-in language engine instantly translates the entire UI, including complex agronomic diagnostic advice, into 6 languages: English, Telugu (తెలుగు), Hindi (हिंदी), Tamil (தமிழ்), Kannada (ಕನ್ನಡ), and Malayalam (മലയാളം)[cite: 3].

---

## 🛠️ Hackathon Transparency Statement

We believe in 100% engineering honesty. Here is exactly how our demonstration operates under the hood:

* **What is REAL:** The Decoupled Architecture, the Open-Meteo API live fetching, the 6-language UI translation engine, the `ntfy.sh` HTTP push notification pipeline, and the dynamic Crop Scorecard logic are all fully functional, production-ready code[cite: 2, 3].
* **What is SIMULATED (For Demo Purposes):** 
  * Because we cannot control the weather during a 5-minute pitch, `edgenode.py` contains a `demo_trigger` with a 10% probability to force an active lightning strike alert to demonstrate our life-safety notification pipeline[cite: 2].
  * Physical soil sensor telemetry (Nitrogen, Phosphorus, Potassium, pH) is emulated by randomly sampling baseline metrics from a local `kaggle_crop_data.csv` dataset, paired with mathematical "sensor noise"[cite: 2, 3].

---

## 🚀 Installation & Usage

### Prerequisites
Ensure Python is installed on your system. Install the required dependencies:
```bash
pip install streamlit pandas requests
Step 1: Test the Alert Pipeline
Before launching the full architecture, ensure your phone is subscribed to the lohith_agri_demo topic on the ntfy app. Run the test script to verify network connectivity:   
PY

Bash
python test_alert.py
If successful, you will receive a test ping on your device.   
PY

Step 2: Boot the Hardware Simulator
Open your first terminal and start the background daemon. Leave this running.

Bash
python edgenode.py
Step 3: Launch the UI
Open a second terminal window and start the frontend Streamlit dashboard.

Bash
streamlit run farmguardapp_04.py
