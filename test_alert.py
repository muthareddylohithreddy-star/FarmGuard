import requests

# Make sure this matches the tab you just opened!
TOPIC = "lohith_agri_demo" 

print(f"🚀 Firing test alert to ntfy.sh/{TOPIC}...")

headers = {
    "Title": "AgriAI Diagnostic Test", 
    "Priority": "urgent", 
    "Tags": "warning,rotating_light"
}

try:
    response = requests.post(f"https://ntfy.sh/{TOPIC}", data="TEST MESSAGE. If you see this, the pipeline works!", headers=headers)
    
    if response.status_code == 200:
        print("✅ SUCCESS! The ntfy server received the message.")
    else:
        print(f"❌ ntfy server rejected it. HTTP Status: {response.status_code}")
        
except Exception as e:
    print(f"❌ CRITICAL NETWORK ERROR. Your Wi-Fi is blocking the signal: {e}")