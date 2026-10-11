import os
from flask import Flask, request
import requests
import google.generativeai as genai

app = Flask(__name__)

# Render Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
    # Yahan apni Page ID aur Page Access Token seedha daal do taaki koi error na aaye!
    page_id = "122105536371497407"  # Apni Page ID yahan likhein
    token = "EAAUW7eZBNlTwBSh09ZBvZAnbmQl3ZAaXylF4y6xEjZCIAU6qTsGCcpu8aZAlMem9kZCHOsBUdrp1oQZCav0jM2XAKupi3YvWXUPC3fZCUoZBJPKwo4rJrtpXCyeK0kiHM9qz0TX2VHsHbs96s7q2mwn1agv9LWE5rr09mfjnbJ9H2G5NZATkjRb1RxPEUigJSgK5ge1vzIq8F4mu1qOZAS3fqaFuhuxjP8GlcDIXQT8qzISZBblhspfZC2jf4fRasQaiVkaAbbp7xOBuFHeVnD9BIZD"    
    sub_url = f"https://graph.facebook.com/v26.0/{page_id}/subscribed_apps?subscribed_fields=messages,messaging_postbacks&access_token={token}"
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
        return response.text
    except Exception:
        return "Namaste! Main abhi aapka message process nahi kar paa raha hoon."

def send_instagram_message(recipient_id, text):
    token = "EAAUW7eZBNlTwBSh09ZBvZAnbmQl3ZAaXylF4y6xEjZCIAU6qTsGCcpu8aZAlMem9kZCHOsBUdrp1oQZCav0jM2XAKupi3YvWXUPC3fZCUoZBJPKwo4rJrtpXCyeK0kiHM9qz0TX2VHsHbs96s7q2mwn1agv9LWE5rr09mfjnbJ9H2G5NZATkjRb1RxPEUigJSgK5ge1vzIq8F4mu1qOZAS3fqaFuhuxjP8GlcDIXQT8qzISZBblhspfZC2jf4fRasQaiVkaAbbp7xOBuFHeVnD9BIZD"
    url = f"https://graph.facebook.com/v20.0/me/messages?access_token={token}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
