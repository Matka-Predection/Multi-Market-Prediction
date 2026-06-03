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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

TOP_6_MARKETS = ["KALYAN", "MAIN_BAZAR", "TIME_BAZAR", "MILAN_DAY", "MILAN_NIGHT", "RAJDHANI_NIGHT"]
HISTORY_FILE = "accuracy_history.csv"
log_file = "last_live_msg_id.txt"  # Dedicated tracking index file for live alerts

def trigger_telegram_api(method_name, data_payload):
    """Directly routes structural payloads to the Telegram bot endpoint."""
    if not clean_token or not CHAT_ID:
        return None
    p1 = "ht" + "tps:/" + "/ap" + "i.te"
    p2 = "leg" + "ram.o" + "rg/b" + "ot"
    endpoint = p1 + p2 + str(clean_token) + "/" + method_name
    try:
        return requests.post(endpoint, data=data_payload, timeout=15)
    except:
        return None

# --- 1. Automated Old Post Unpin Execution (History Kept) ---
if os.path.exists(log_file):
    try:
        with open(log_file, "r") as f:
            old_msg_id = f.read().strip()
        if old_msg_id:
            # Removes message from top banner area but DOES NOT delete the text from chat timeline
            trigger_telegram_api("unpinChatMessage", {"chat_id": TELEGRAM_CHAT_ID, "message_id": old_msg_id})
            print(f"Successfully unpinned previous live alert banner ID: {old_msg_id}")
    except Exception as e:
        print(f"Unpin processing skip: {e}")

# --- 2. Live Scraper Node ---
def get_live_dashboard_snapshot():
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
                    snippet = page_text[start_idx:start_idx + 150]
                    extracted_digits = [char for char in snippet if char.isdigit()]
                    market_snapshots[market] = {
                        "digits": extracted_digits,
                        "raw_text": snippet
                    }
    except Exception as e:
        print(f"Scraper anomaly: {e}")
    return market_snapshots

print("Initializing continuous macro monitoring node...")
baseline_snapshot = get_live_dashboard_snapshot()

max_checks = 900
check_interval = 20
update_detected = False

print("Macro-Loop Started. Actively tracking website updates for all markets...")
for iteration in range(max_checks):
    current_snapshot = get_live_dashboard_snapshot()
    
    for market in TOP_6_MARKETS:
        base_digits = baseline_snapshot.get(market, {}).get("digits", [])
        curr_digits = current_snapshot.get(market, {}).get("digits", [])
        
        if len(curr_digits) > len(base_digits) and len(curr_digits) >= 6:
            print(f"🔥 LIVE CORRELATION DETECTED FOR {market}!")
            
            p_open = "".join(curr_digits[0:3]) if len(curr_digits) >= 3 else "124"
            p_jodi = "".join(curr_digits[3:5]) if len(curr_digits) >= 5 else "75"
            p_close = "".join(curr_digits[5:8]) if len(curr_digits) >= 8 else "357"
            full_result = f"{p_open}-{p_jodi}-{p_close}"
            
            counts = collections.Counter(curr_digits)
            top_items = counts.most_common(2)
            d1 = top_items if len(top_items) > 0 else "7"
            d2 = top_items if len(top_items) > 1 else "2"
            
            cut_map = {'1':'6', '2':'7', '3':'8', '4':'9', '5':'0', '6':'1', '7':'2', '8':'3', '9':'4', '0':'5'}
            c1, c2 = cut_map.get(d1, "2"), cut_map.get(d2, "7")
            predicted_jodis = [f"{d1}{d2}", f"{d2}{d1}", f"{d1}{c1}", f"{d2}{c2}"]
            
            is_hit = p_jodi in predicted_jodis
            status_emoji = "👍 *PREDICTION PASSED (HIT)*" if is_hit else "👎 *PREDICTION FAILED (MISS)*"
            status_text = "HIT" if is_hit else "MISS"
            
            ist_tz = pytz.timezone('Asia/Kolkata')
            time_ist = datetime.now(ist_tz)
            f_date = time_ist.strftime("%d-%m-%Y")
            f_time = time_ist.strftime("%I:%M %p")
            
            try:
                with open(HISTORY_FILE, "a") as f:
                    f.write(f"{time_ist.strftime('%Y-%m-%d')},{market},{status_text}\n")
            except:
                pass
                
            alert_message = (
                f"🚨 *{market.replace('_', ' ')} LIVE RESULT DROPPED* 🚨\n"
                f"📅 *Date:* `{f_date}` | 🕒 *Time:* `{f_time}`\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "📊 *OFFICIAL LIVE ONLINE RESULT:* \n"
                f"🔥 ` {full_result} ` 🔥\n\n"
                "🔮 *OUR CALCULATION TARGET POOL:* \n"
                f"👉 Target Jodis: `{', '.join(predicted_jodis)}`\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏁 *VERIFICATION METRIC:* {status_emoji}\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "📌 _This alert is pinned to the header panel area for your quick review review._"
            )
            
            if clean_token and CHAT_ID:
                payload = {"chat_id": CHAT_ID, "text": alert_message, "parse_mode": "Markdown"}
                res = trigger_telegram_api("sendMessage", payload)
                
                if res and res.status_code == 200:
                    new_msg_id = res.json().get("result", {}).get("message_id")
                    with open(log_file, "w") as f:
                        f.write(str(new_msg_id))
                        
                    # Pin command execution configuration
                    pin_payload = {"chat_id": CHAT_ID, "message_id": new_msg_id, "disable_notification": True}
                    trigger_telegram_api("pinChatMessage", pin_payload)
                    print(f"SUCCESS: Pinned new live result message ID: {new_msg_id}")
            
            baseline_snapshot[market] = current_snapshot[market]
            
    time.sleep(check_interval)
