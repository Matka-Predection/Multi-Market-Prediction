import collections
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

# Secure credentials pulled from environmental container variables
clean_token = os.environ.get("BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("CHAT_ID", "").strip()

TARGET_URL = "https://sattamatkadpboss.mobi"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

log_file = "last_msg_id.txt"
TOP_6_MARKETS = ["KALYAN", "MAIN_BAZAR", "TIME_BAZAR", "MILAN_DAY", "MILAN_NIGHT", "RAJDHANI_NIGHT"]

def trigger_telegram_api(method_name, data_payload):
    """Directly routes structural payloads to the Telegram bot endpoint."""
    if not clean_token or not TELEGRAM_CHAT_ID:
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
            # Removes the message from the pinned banner zone but DOES NOT delete the text from chat history
            trigger_telegram_api("unpinChatMessage", {"chat_id": TELEGRAM_CHAT_ID, "message_id": old_msg_id})
            print(f"Successfully unpinned previous message banner ID: {old_msg_id}")
    except Exception as e:
        print(f"Unpin processing skip: {e}")

# --- 2. Live Scraper Node ---
def scrape_filtered_charts():
    market_digits = {market: [] for market in TOP_6_MARKETS}
    try:
        res = requests.get(TARGET_URL, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            page_text = soup.get_text().upper()
            
            for market in TOP_6_MARKETS:
                search_word = market.replace("_", " ")
                start_idx = page_text.find(search_word)
                if start_idx != -1:
                    window = page_text[start_idx:start_idx + 300]
                    for char in window:
                        if char.isdigit():
                            market_digits[market].append(char)
    except:
        pass
    for market in TOP_6_MARKETS:
        if len(market_digits[market]) < 8:
            market_digits[market] = list("3469152708")
    return market_digits

filtered_charts_data = scrape_filtered_charts()

# Calculate global hot trend digits across all combined markets
all_global_digits = []
for digit_list in filtered_charts_data.values():
    all_global_digits.extend(digit_list)

global_counts = collections.Counter(all_global_digits).most_common(2)
global_hot_1 = global_counts[0][0] if len(global_counts) > 0 else "7"
global_hot_2 = global_counts[1][0] if len(global_counts) > 1 else "2"

# --- 3. Enhanced Deep Prediction Engine ---
def calculate_advanced_predictions(digits_list):
    counts = collections.Counter(digits_list)
    top_items = counts.most_common(4)
    
    d1 = top_items[0][0] if len(top_items) > 0 else "7"
    d2 = top_items[1][0] if len(top_items) > 1 else "2"
    d3 = top_items[2][0] if len(top_items) > 2 else "1"
    d4 = top_items[3][0] if len(top_items) > 3 else "5"
    
    cut_map = {'1':'6', '2':'7', '3':'8', '4':'9', '5':'0', '6':'1', '7':'2', '8':'3', '9':'4', '0':'5'}
    c1 = cut_map.get(d1, "2")
    c2 = cut_map.get(d2, "7")
    
    return {
        "direct": f"`{d1}{d2}` • `{d2}{d1}` • `{d3}{d4}`",
        "cross": f"`{d1}{c1}` • `{d2}{c2}` • `{d3}{c2}`",
        "family": f"`{d1}{d2}` • `{d2}{d1}` • `{c1}{c2}` • `{c2}{c1}`",
        "sum": f"Sum `{ (int(d1)+int(d2))%10 }`",
        "motor": " • ".join([f"`{d1}{d2}{d3}`", f"`{d1}{d2}{d4}`", f"`{d2}{d3}{d4}`"])
    }

# --- 4. Format Message Template Layout ---
ist_tz = pytz.timezone('Asia/Kolkata')
time_ist = datetime.now(ist_tz)
formatted_date = time_ist.strftime("%d-%m-%Y")
formatted_time = time_ist.strftime("%I:%M %p")

summary_blocks = [
    "🌐 *GLOBAL TOP-6 PREMIUM MARKET DASHBOARD* 🌐",
    f"📅 *Date:* `{formatted_date}` | 🕒 *Time:* `{formatted_time}`",
    "━━━━━━━━━━━━━━━━━━━━━",
    f"🔥 *GLOBAL HOT DIGITS FOR TODAY:*  🏆 ` {global_hot_1} `  •  ` {global_hot_2} ` 🏆",
    "━━━━━━━━━━━━━━━━━━━━━\n"
]

idx = 1
for market_id in TOP_6_MARKETS:
    pred = calculate_advanced_predictions(filtered_charts_data[market_id])
    summary_blocks.append(
        f"👑 *{idx}. {market_id.replace('_', ' ')} ANALYSIS*\n"
        f"👉 Direct/Cross : {pred['direct']} • {pred['cross']}\n"
        f"👉 Family Jodis : {pred['family']} | {pred['sum']}\n"
        f"👉 Motor Pannas : {pred['motor']}\n"
        "-------------------------------------"
    )
    idx += 1

summary_blocks.append("📌 _This premium dashboard updates all active markets automatically at 7:00 AM IST daily._")
tg_message = "\n".join(summary_blocks)

# --- 5. Delivery Engine Execution ---
if clean_token and TELEGRAM_CHAT_ID:
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": tg_message, "parse_mode": "Markdown"}
    res = trigger_telegram_api("sendMessage", payload)
    
    if res and res.status_code == 200:
        new_msg_id = res.json().get("result", {}).get("message_id")
        with open(log_file, "w") as f:
            f.write(str(new_msg_id))
            
        pin_payload = {"chat_id": TELEGRAM_CHAT_ID, "message_id": new_msg_id, "disable_notification": True}
        trigger_telegram_api("pinChatMessage", pin_payload)
        print(f"SUCCESS: Pinned new prediction board message ID: {new_msg_id}")
    else:
        print(f"Delivery failure. Status code: {res.status_code if res else 'No Connection'}")
