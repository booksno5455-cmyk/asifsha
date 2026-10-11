import os
from flask import Flask, request
import requests
import google.generativeai as genai

app = Flask(__name__)

# Render Environment Variables (Render se apne aap token utha lega)
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_secret_token_123")

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Custom AI System Instruction
SYSTEM_PROMPT = """
Tum instagram profile @mak_07s___ (Mr. Asif) ke smart AI assistant ho.

Niyam:
1. Pehchan: Tum kabhi bhi apna naam 'Gemini' ya 'Google AI' nahi bataoge. Agar koi puche ki tum kon ho, toh kaho ki tum Mr. Asif ke dwara banaye gaye unke smart AI assistant ho.
2. Bhasha: User jis bhasha me message kare (Hindi, Hinglish, ya English), usi bhasha me bohot hi vinamrata aur doostana andaz me jawab do.
3. Tarif aur jaankari: Mr. Asif aur unki instagram ID @mak_07s___ ki prashansa karo. Batao ki Asif bohot hi shandar content banate hain aur Lucknow se hain.
4. Sahayata: User ke har sawal ka satik, chota aur upyogi jawab do.
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
    data = request.get_json()
    if data.get('object') in ['page', 'instagram']:
        for entry in data.get('entry', []):
            for messaging in entry.get('messaging', []):
                sender_id = messaging.get('sender', {}).get('id')
                message_text = messaging.get('message', {}).get('text')
                if sender_id and message_text:
                    reply = get_gemini_reply(message_text)
                    send_instagram_message(sender_id, reply)
    return 'OK', 200

@app.route('/auto-subscribe', methods=['GET'])
def auto_subscribe():
    token = os.getenv("PAGE_ACCESS_TOKEN")
    if not token:
        return {"error": "PAGE_ACCESS_TOKEN environment variable is missing!"}, 400
    
    # 1. Automatically fetch Page ID using the token
    me_url = f"https://graph.facebook.com/v26.0/me?access_token={token}"
    res_me = requests.get(me_url).json()
    
    if "id" not in res_me:
        return {"error": "Could not fetch Page ID from Meta", "details": res_me}, 400
        
    page_id = res_me["id"]
    
    # 2. Automatically Subscribe the Webhook
    sub_url = f"https://graph.facebook.com/v26.0/{page_id}/subscribed_apps?subscribed_fields=messages,messaging_postbacks&access_token={token}"
    res_sub = requests.post(sub_url).json()
    
    return {
        "status": "Success",
        "page_id": page_id,
        "subscription_result": res_sub
    }

def get_gemini_reply(user_message):
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser message: {user_message}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception:
        return "Namaste! Main abhi aapka message process nahi kar paa raha hoon."

def send_instagram_message(recipient_id, text):
    url = f"https://graph.facebook.com/v20.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
