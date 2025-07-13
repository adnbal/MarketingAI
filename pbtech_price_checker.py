import pandas as pd
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load Twilio credentials from .env file
load_dotenv()
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Scraper function
def get_pbtech_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        price_tag = soup.find("span", class_="price")
        if price_tag:
            return float(price_tag.text.replace("$", "").replace(",", "").strip())
        meta = soup.find("meta", itemprop="price")
        if meta and meta.get("content"):
            return float(meta["content"])
    except:
        return None
    return None

# SMS function
def send_sms(to_number, message):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=FROM_NUMBER,
        to=to_number
    )

# Main CSV-based scheduler
def run_scheduler(csv_path="pbtech_price_watch_schedule.csv"):
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        url = row["product_url"]
        target_price = float(row["target_price"])
        phone = f"+{int(row['phone_number'])}"
        current_price = get_pbtech_price(url)

        print(f"Checking {url} → Price: {current_price}")
        if current_price and current_price <= target_price:
            message = f"📢 PBTech Deal Alert: ${current_price}\n{url}"
            send_sms(phone, message)
            print(f"✅ SMS sent to {phone}")
        else:
            print("No alert sent.")

# Entry point
if __name__ == "__main__":
    run_scheduler()
