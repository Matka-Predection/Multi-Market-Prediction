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

print("Compiling weekly metric report card...")

total_runs = 0
hits = 0
misses = 0

if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r") as f:
            lines = f.readlines()[1:] # Skip header
            for line in lines:
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) >= 3:
                        res = parts[2]
                        total_runs += 1
                        if res == "HIT":
                            hits += 1
                        else:
                            misses += 1
    except Exception as e:
        print(f"Error parsing log file: {e}")

# Calculate precise accuracy rate
accuracy_rate = (hits / total_runs * 100) if total_runs > 0 else 0.0

ist_tz = pytz.timezone('Asia/Kolkata')
time_ist = datetime.now(ist_tz)
formatted_date = time_ist.strftime("%d-%m-%Y")

# Build the card template
report_card = (
    "📈 *WEEKLY SYSTEM ACCURACY REPORT CARD* 📈\n"
    f"📅 *Week Ending Date:* `{formatted_date}`\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"🏆 *OVERALL PERFORMANCE RATE:* ` {accuracy_rate:.1f}% `\n\n"
    f"📊 *Statistical Summary parameters:*\n"
    f"👉 Total Evaluated Sessions: `{total_runs}`\n"
    f"👉 Accurate Targets (HITS) 👍: `{hits}`\n"
    f"👉 Deflected Targets (MISSES) 👎: `{misses}`\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🎯 _The mathematical engine resets its metrics tracking matrix now for the upcoming week cycle._"
)

if clean_token and CHAT_ID and total_runs > 0:
    payload = {"chat_id": CHAT_ID, "text": report_card, "parse_mode": "Markdown"}
    requests.post("https://telegram.org" + clean_token + "/sendMessage", data=payload)
    
    # Reset history file for the next week
    try:
        os.remove(HISTORY_FILE)
        print("Metrics file wiped and reset for next week.")
    except Exception as e:
        print(f"Reset skip: {e}")
else:
    print("No evaluated history lines logged this week to calculate stats.")
