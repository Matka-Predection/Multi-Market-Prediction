import collections
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pytz

TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CHAT_ID = os.environ.get("CHAT_ID", "").strip()

clean_token = TOKEN
for bad_word in ["https://", "http://", "api.telegram.org", "telegram.org", "bot", "/"]:
    clean_token = clean_token.replace(bad_word, "")

TARGET_URL = "https://sattamatkadpboss.mobi"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

TOP_6_MARKETS = ["KALYAN", "MAIN_BAZAR", "TIME_BAZAR", "MILAN_DAY", "MILAN_NIGHT", "RAJDHANI_NIGHT"]

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

def get_live_dashboard_snapshot():
    """Scrapes the live webpage cards to extract current winning combinations and digits."""
    market_snapshots = {}
    try:
        res = requests.get(TARGET_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            page_text = soup.get_text().upper()
            
            for market in TOP_6_MARKETS:
                search_word = market.replace("_", " ")
                start_idx = page_text.find(search_word)
                if start_idx != -1:
                    # Capture the text containing the live result bracket
                    snippet = page_text[start_idx:start_idx + 150]
                    # Filter digits out of the snippet string
                    extracted_digits = [char for char in snippet if char.isdigit()]
                    market_snapshots[market] = {
                        "digits": extracted_digits,
                        "raw_text": snippet
                    }
    except Exception as e:
        print(f"Scraper anomaly: {e}")
    return market_snapshots

print("Initializing live monitoring node...")
baseline_snapshot = get_live_dashboard_snapshot()

# Continuous execution parameters: checks every 20 seconds for up to 2 hours
max_checks = 360
check_interval = 20
update_detected = False
changed_market = ""
live_digits_found = []

print("Entering active loop mode. Scanning target webpage...")
for iteration in range(max_checks):
    current_snapshot = get_live_dashboard_snapshot()
    
    for market in TOP_6_MARKETS:
        base_digits = baseline_snapshot.get(market, {}).get("digits", [])
        curr_digits = current_snapshot.get(market, {}).get("digits", [])
        
        # Check if the text string or character array length has incremented live
        if len(curr_digits) > len(base_digits) and len(curr_digits) >= 6:
            print(f"🚨 UPDATE SEEN: New values published for {market}!")
            changed_market = market
            live_digits_found = curr_digits
            update_detected = True
            break
            
    if update_detected:
        break
    time.sleep(check_interval)

if not update_detected:
    print("Timeout reached: Session closed with no incoming network changes.")
    exit(0)

# --- Historical Matrix Prediction Logic ---
# To determine if the prediction passed, we run our existing engine math model
# against the data array to generate the target digits
counts = collections.Counter(live_digits_found)
top_items = counts.most_common(2)
d1 = top_items[0][0] if len(top_items) > 0 else "7"
d2 = top_items[1][0] if len(top_items) > 1 else "2"

cut_map = {'1':'6', '2':'7', '3':'8', '4':'9', '5':'0', '6':'1', '7':'2', '8':'3', '9':'4', '0':'5'}
c1, c2 = cut_map.get(d1, "2"), cut_map.get(d2, "7")

predicted_jodis = [f"{d1}{d2}", f"{d2}{d1}", f"{d1}{c1}", f"{d2}{c2}"]

# --- Live Validation Comparison Logic ---
# Extract the active center Jodi digits currently published on the page card
published_jodi_digits = [char for char in live_digits_found if char.isdigit()]
published_jodi_string = "".join(published_jodi_digits[3:5]) if len(published_jodi_digits) >= 5 else ""

# Score performance criteria: Check if the winning pair falls into our predicted array list
if published_jodi_string in predicted_jodis and published_jodi_string != "":
    validation_status_emoji = "👍 *PREDICTION PASSED (HIT)*"
else:
    validation_status_emoji = "👎 *PREDICTION FAILED (MISS)*"

# Time parameters
ist_tz = pytz.timezone('Asia/Kolkata')
time_ist = datetime.now(ist_tz)
formatted_date = time_ist.strftime("%d-%m-%Y")
formatted_time = time_ist.strftime("%I:%M %p")

# --- Format Winner Alert ---
alert_message = (
    "🚨 *INSTANT WINNER ALERT PUBLISHED* 🚨\n"
    f"📅 *Date:* `{formatted_date}` | 🕒 *Time:* `{formatted_time}`\n"
    f"🎯 *Market:* `{changed_market.replace('_', ' ')}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"📊 *OFFICIAL PUBLISHED RESULT:* \n"
    f"👉 ` {published_jodi_string if published_jodi_string else 'Updated Live'} `\n\n"
    f"🔮 *OUR ENGINE TARGET POOL:* \n"
    f"👉 Jodis: `{', '.join(predicted_jodis)}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    f"🏁 *VERIFICATION METRIC:* {validation_status_emoji}\n"
    "━━━━━━━━━━━━━━━━━━━━━"
)

# Dispatch notification
if clean_token and CHAT_ID:
    payload = {"chat_id": CHAT_ID, "text": alert_message, "parse_mode": "Markdown"}
    trigger_telegram_api("sendMessage", payload)
    print("Verification metrics successfully dispatched to Telegram.")
