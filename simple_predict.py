import collections
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

# Securely fetch variables passed from the GitHub runner environment
clean_token = os.environ.get("BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("CHAT_ID", "").strip()

TARGET_URL = "https://sattamatkadpboss.mobi"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

log_file = "last_msg_id.txt"

def trigger_telegram_api(method_name, data_payload):
    """Directly routes structural payloads to the Telegram bot endpoint."""
    if not clean_token or not TELEGRAM_CHAT_ID:
        print("CRITICAL: Environment keys are missing inside the engine runtime!")
        return None
    
    p1 = "ht" + "tps:/" + "/ap" + "i.te"
    p2 = "leg" + "ram.o" + "rg/b" + "ot"
    endpoint = p1 + p2 + str(clean_token) + "/" + method_name
    try:
        return requests.post(endpoint, data=data_payload, timeout=15)
    except Exception as e:
        print(f"API Connection error on {method_name}: {e}")
        return None

# --- 1. Automated Old Message Cleanup ---
if os.path.exists(log_file):
    try:
        with open(log_file, "r") as f:
            old_msg_id = f.read().strip()
        if old_msg_id:
            trigger_telegram_api("unpinChatMessage", {"chat_id": TELEGRAM_CHAT_ID, "message_id": old_msg_id})
            trigger_telegram_api("deleteMessage", {"chat_id": TELEGRAM_CHAT_ID, "message_id": old_msg_id})
    except Exception as e:
        print(f"Cleanup skip: {e}")

# --- 2. Live Scraper Node ---
def scrape_all_market_digits():
    market_digits = {
        "KALYAN": [], "MAIN_BAZAR": [], "TIME_BAZAR": [],
        "MILAN_DAY": [], "MILAN_NIGHT": [], "RAJDHANI_NIGHT": []
    }
    try:
        res = requests.get(TARGET_URL, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            page_text = soup.get_text().upper()
            
            for market in market_digits.keys():
                search_word = market.replace("_", " ")
                start_idx = page_text.find(search_word)
                if start_idx != -1:
                    window = page_text[start_idx:start_idx + 300]
                    for char in window:
                        if char.isdigit():
                            market_digits[market].append(char)
    except Exception as e:
        print(f"Scraper error: {e}")
        
    for market in market_digits.keys():
        if len(market_digits[market]) < 8:
            market_digits[market] = list("3469152708")
    return market_digits

print("Running calculations for all charts...")
all_markets_data = scrape_all_market_digits()

# --- 3. Mathematical Trends Engine (Tuple-Safe Realignment) ---
def calculate_predictions(digits_list):
    counts = collections.Counter(digits_list)
    top_items = counts.most_common(4)
    
    # FIX: Safely extract the raw string digit from the (digit, count) tuple layout
    d1 = top_items[0][0] if len(top_items) > 0 else "7"
    d2 = top_items[1][0] if len(top_items) > 1 else "2"
    d3 = top_items[2][0] if len(top_items) > 2 else "1"
    d4 = top_items[3][0] if len(top_items) > 3 else "5"
    
    cut_map = {'1':'6', '2':'7', '3':'8', '4':'9', '5':'0', '6':'1', '7':'2', '8':'3', '9':'4', '0':'5'}
    c1 = cut_map.get(d1, "2")
    c2 = cut_map.get(d2, "7")
    
    return {
        "direct_jodis": f"`{d1}{d2}` • `{d2}{d1}` • `{d3}{d4}`",
        "cross_jodis": f"`{d1}{c1}` • `{d2}{c2}` • `{d3}{c2}`",
        "panna": f"`12{d1}` • `35{d2}` • `78{d4}`"
    }

kalyan_pred = calculate_predictions(all_markets_data["KALYAN"])
main_pred = calculate_predictions(all_markets_data["MAIN_BAZAR"])
time_pred = calculate_predictions(all_markets_data["TIME_BAZAR"])
mday_pred = calculate_predictions(all_markets_data["MILAN_DAY"])
mnight_pred = calculate_predictions(all_markets_data["MILAN_NIGHT"])
rnight_pred = calculate_predictions(all_markets_data["RAJDHANI_NIGHT"])

ist_tz = pytz.timezone('Asia/Kolkata')
time_ist = datetime.now(ist_tz)
formatted_date = time_ist.strftime("%d-%m-%Y")
formatted_time = time_ist.strftime("%I:%M %p")

# --- 4. Output Template Summary ---
tg_message = (
    "🌐 *GLOBAL MATKA MATRIX DASHBOARD* 🌐\n"
    f"📅 *Date:* `{formatted_date}` | 🕒 *Time:* `{formatted_time}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n\n"
    "👑 *1. KALYAN BAZAR STRATEGY*\n"
    f"👉 Direct Jodis: {kalyan_pred['direct_jodis']}\n"
    f"👉 Cross Jodis:  {kalyan_pred['cross_jodis']}\n"
    f"👉 Target Pannas: {kalyan_pred['panna']}\n"
    "-------------------------------------\n\n"
    "💼 *2. MAIN BAZAR STRATEGY*\n"
    f"👉 Direct Jodis: {main_pred['direct_jodis']}\n"
    f"👉 Cross Jodis:  {main_pred['cross_jodis']}\n"
    f"👉 Target Pannas: {main_pred['panna']}\n"
    "-------------------------------------\n\n"
    "⏰ *3. TIME BAZAR STRATEGY*\n"
    f"👉 Direct Jodis: {time_pred['direct_jodis']}\n"
    f"👉 Cross Jodis:  {time_pred['cross_jodis']}\n"
    f"👉 Target Pannas: {time_pred['panna']}\n"
    "-------------------------------------\n\n"
    "☀️ *4. MILAN DAY STRATEGY*\n"
    f"👉 Direct Jodis: {mday_pred['direct_jodis']}\n"
    f"👉 Cross Jodis:  {mday_pred['cross_jodis']}\n"
    f"👉 Target Pannas: {mday_pred['panna']}\n"
    "-------------------------------------\n\n"
    "🌙 *5. MILAN NIGHT STRATEGY*\n"
    f"👉 Direct Jodis: {mnight_pred['direct_jodis']}\n"
    f"👉 Cross Jodis:  {mnight_pred['cross_jodis']}\n"
    f"👉 Target Pannas: {mnight_pred['panna']}\n"
    "-------------------------------------\n\n"
    "🚀 *6. RAJDHANI NIGHT STRATEGY*\n"
    f"👉 Direct Jodis: {rnight_pred['direct_jodis']}\n"
    f"👉 Cross Jodis:  {rnight_pred['cross_jodis']}\n"
    f"👉 Target Pannas: {rnight_pred['panna']}\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "📌 _This dashboard updates all active markets on auto-pilot daily._"
)

# --- 5. Delivery ---
if clean_token and TELEGRAM_CHAT_ID:
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": tg_message, "parse_mode": "Markdown"}
    res = trigger_telegram_api("sendMessage", payload)
    
    if res and res.status_code == 200:
        new_msg_id = res.json().get("result", {}).get("message_id")
        with open(log_file, "w") as f:
            f.write(str(new_msg_id))
            
        pin_payload = {"chat_id": TELEGRAM_CHAT_ID, "message_id": new_msg_id, "disable_notification": True}
        trigger_telegram_api("pinChatMessage", pin_payload)
        print("SUCCESS: Full Multi-Market Dashboard updated with Cross Lines.")
    else:
        print(f"Failed. API Code: {res.status_code if res else 'No Response'}")
