from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

YALIDINE_ALERT_STATUSES = [
    "Retour vers centre",
    "Tentative échouée",
    "Client ne répond pas",
    "Client no-show",
    "En attente du client",
    "Annulé par le client",
    "Echèc livraison"
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = data.get('type', '')

    if event_type == 'parcel_status_updated':
        events = data.get('events', [])
        for event in events:
            event_data = event.get('data', {})
            tracking = event_data.get('tracking', 'N/A')
            status = event_data.get('status', 'N/A')
            reason = event_data.get('reason', '')

            if status in YALIDINE_ALERT_STATUSES:
                reason_line = f"\n📝 السبب: <i>{reason}</i>" if reason else ""
                message = f"""
🚚 <b>Yalidine Express</b>
⚠️ <b>تنبيه طرد</b>
━━━━━━━━━━━━━━
📬 رقم التتبع: <code>{tracking}</code>
📊 الحالة: <b>{status}</b>{reason_line}
                """
                send_telegram(message)

    return {"status": "ok"}, 200

@app.route('/', methods=['GET'])
def home():
    return "✅ Yalidine Webhook server is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
