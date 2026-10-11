import os
from flask import Flask, request
import requests
import google.generativeai as genai

app = Flask(__name__)

# Render Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PAGE_ACCESS_TOKEN = "IGAAr3oqq5zuJBZAGFlUHVqUlRhdmpKVUxZAa0lJdUN1WVpSTmZAMS3daelZAmV3R5RTZAPY2RTZAVpyaWVUOTFpcWxmc3N5cUw1OVJXSW5aUXliOENqdUpWZADNXc3VnY2I1R3pWQlNuOUdzTXVFeF9CQkZAYZAzRoc19mcUdINmNkVEtpVQZDZD"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_secret_token_123")

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = """
Tum instagram profile @mak_07s___ (Mr. Asif) ke smart AI assistant ho.
Niyam:
1. Pehchan: Tum kabhi bhi apna naam 'Gemini' ya 'Google AI' nahi bataoge. Kaho ki tum Mr. Asif ke dwara banaye gaye unke smart AI assistant ho.
2. Bhasha: User jis bhasha me message kare, usi bhasha me vinamrata aur dostana andaz me jawab do.
3. Tarif: Mr. Asif aur unki instagram ID @mak_07s___ ki prashansa karo ki woh shandar content banate hain aur Lucknow se hain.
4. Sahayata: Har sawal ka satik, chota aur upyogi jawab do.
"""

@app.route('/')
def home():
    return "Asif ka Instagram AI Bot Live Hai! 🚀", 200

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    # Sabse pehle dekhenge ki Meta se asli data kya aa raha hai
    raw_data = request.data.decode('utf-8')
    print("🔥 RAW INSTAGRAM DATA:", raw_data)
    
    data = request.get_json(silent=True)
    if not data:
        print("⚠️ JSON parse nahi ho paya!")
        return 'OK', 200
    
    try:
        if data.get('object') in ['page', 'instagram']:
            for entry in data.get('entry', []):
                messaging_events = entry.get('messaging', [])
                
                # Agar messaging khali hai toh changes check karo
                if not messaging_events and 'changes' in entry:
                    for change in entry.get('changes', []):
                        if change.get('field') == 'messages':
                            val = change.get('value', {})
                            if val:
                                messaging_events.append(val)
                
                for messaging in messaging_events:
                    sender_id = messaging.get('sender', {}).get('id')
                    # Kuch formats me 'sender' ki jagah 'from' hota hai
                    if not sender_id:
                        sender_id = messaging.get('from', {}).get('id')
                        
                    message_text = messaging.get('message', {}).get('text')
                    
                    if sender_id and message_text:
                        print(f"✅ Message mil gaya! Sender ID: {sender_id}, Text: {message_text}")
                        reply = get_gemini_reply(message_text)
                        send_instagram_message(sender_id, reply)
                    else:
                        print("⚠️ Sender ID ya Message Text nahi mila is event me.")
    except Exception as e:
        print("❌ Webhook ke andar error aa gaya:", e)
        
    return 'OK', 200

@app.route('/auto-subscribe', methods=['GET'])
def auto_subscribe():
    page_id = "122105536371497407"
    sub_url = f"https://graph.facebook.com/v26.0/{page_id}/subscribed_apps?subscribed_fields=messages,messaging_postbacks&access_token={PAGE_ACCESS_TOKEN}"
    res_sub = requests.post(sub_url).json()
    return {
        "status": "Attempted",
        "page_id": page_id,
        "subscription_result": res_sub
    }

def get_gemini_reply(user_message):
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser message: {user_message}"
        response = model.generate_content(full_prompt)
        print("🤖 Gemini ne jawab de diya:", response.text)
        return response.text
    except Exception as e:
        print("❌ Gemini Error:", e)
        return "Namaste! Main abhi aapka message process nahi kar paa raha hoon."

def send_instagram_message(recipient_id, text):
    url = f"https://graph.facebook.com/v26.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    response = requests.post(url, json=payload, headers=headers)
    print("📤 Instagram Send Response:", response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
