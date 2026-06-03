import os
import requests
from datetime import datetime
import pytz

TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

clean_token = TOKEN
for bad_word in ["https://", "http://", "api.telegram.org", "telegram.org", "bot", "/"]:
    clean_token = clean_token.replace(bad_word, "")

HISTORY_FILE = "accuracy_history.csv"

def trigger_telegram_api(method_name, data_payload):
    if not clean_token or not CHAT_ID:
        return None
    p1 = "ht" + "tps:/" + "/ap" + "i.te"
    p2 = "leg" + "ram.o" + "rg/b" + "ot"
    endpoint = p1 + p2 + str(clean_token) + "/" + method_name
    try:
        return requests.post(endpoint, data=data_payload, timeout=15)
    except:
        return None

print("Compiling customized premium report card...")

total_runs = 0
hits = 0
misses = 0

if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r") as f:
            lines = f.readlines()[1:] # Skip header row
            for line in lines:
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) >= 3:
                        res = parts[2].strip()
                        total_runs += 1
                        if res == "HIT":
                            hits += 1
                        else:
                            misses += 1
    except Exception as e:
        print(f"Error parsing log file: {e}")

# Calculate metrics
accuracy_rate = (hits / total_runs * 100) if total_runs > 0 else 0.0

# Performance Badge Assignment
if accuracy_rate >= 80:
    badge = "🏆 *EXCELLENT WEEK (VIP GRADE)*"
elif accuracy_rate >= 50:
    badge = "📈 *STABLE PERFORMANCE (STANDARD GRADE)*"
else:
    badge = "📉 *VOLATILE TRACK (ADJUSTMENT NEEDED)*"

ist_tz = pytz.timezone('Asia/Kolkata')
time_ist = datetime.now(ist_tz)
formatted_date = time_ist.strftime("%d-%m-%Y")

# --- Premium Layout Card Configuration ---
report_card = (
    "🎰 *MATKA BAZAAR WEEKLY ACCURACY REPORT CARD* 🎰\n"
    f"📅 *Week Ending:* `{formatted_date}`\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    f"🌟 *Current Status:* {badge}\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"🎯 *ACCURACY RATE ACCELERATOR:*\n"
    f"⚡ ` {accuracy_rate:.1f}% SUCCESS PERFORMANCE ` ⚡\n\n"
    f"📋 *TRACKING MATRIX METRICS:*\n"
    f"🔹 Total Sessions Evaluated : `{total_runs}`\n"
    f"🟢 Successful Predictions (HITS)  : `{hits}` 👍\n"
    f"🔴 Unsuccessful Predictions (MISS) : `{misses}` 👎\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🔄 _The historical calculation database has reset for the upcoming session cycle._"
)

if clean_token and CHAT_ID and total_runs > 0:
    payload = {"chat_id": CHAT_ID, "text": report_card, "parse_mode": "Markdown"}
    res = trigger_telegram_api("sendMessage", payload)
    if res and res.status_code == 200:
        print("Premium card delivered successfully.")
    
    # Wipe tracking sheet cleanly for the upcoming week cycle
    try:
        os.remove(HISTORY_FILE)
    except:
        pass
else:
    # Fallback mockup for direct testing when the log sheet is still blank
    mock_card = (
        "📊 *WEEKLY PERFORMANCE ACCURACY REPORT* 📊\n"
        f"📅 *Week Ending:* `{formatted_date}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🌟 *Current Status:* 🏆 *EXCELLENT WEEK (VIP GRADE)*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 *ACCURACY RATE ACCELERATOR:*\n"
        "⚡ ` 85.5% SUCCESS PERFORMANCE ` ⚡\n\n"
        "📋 *TRACKING MATRIX METRICS:*\n"
        "🔹 Total Sessions Evaluated : `20`\n"
        "🟢 Successful Predictions (HITS)  : `17` 👍\n"
        "🔴 Unsuccessful Predictions (MISS) : `3` 👎\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🧪 _[TEST RUN MODE]: Send /start to activate tracking logs._"
    )
    payload = {"chat_id": CHAT_ID, "text": mock_card, "parse_mode": "Markdown"}
    trigger_telegram_api("sendMessage", payload)
