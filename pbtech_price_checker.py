import requests
from bs4 import BeautifulSoup
import pandas as pd
from twilio.rest import Client

# 🔑 Twilio credentials (use env vars or config for real deployment)
ACCOUNT_SID = "your_twilio_sid"
AUTH_TOKEN = "your_twilio_auth_token"
FROM_NUMBER = "+1234567890"  # Twilio phone number

def get_pbtech_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    price_tag = soup.select_one("meta[itemprop='price']")  # PBTech uses schema.org
    if price_tag:
        try:
            return float(price_tag['content'])
        except:
            return None
    return None

def send_sms(to_number, message):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=FROM_NUMBER,
        to=to_number
    )

def run_scheduler(csv_path):
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        url = row['product_url']
        target_price = float(row['target_price'])
        phone = f"+{int(row['phone_number'])}"

        current_price = get_pbtech_price(url)
        print(f"🔍 Checking {url} → Current: ${current_price}")

        if current_price and current_price <= target_price:
            msg = f"💰 Deal Alert! Price dropped to ${current_price} at PBTech.\n{url}"
            send_sms(phone, msg)
            print(f"📲 SMS sent to {phone}")
        else:
            print("🕒 No alert sent — price above threshold.")

# Run it
run_scheduler("pbtech_price_watch_schedule.csv")
