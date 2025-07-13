import streamlit as st
from twilio.rest import Client
import requests
from bs4 import BeautifulSoup

# Set up Streamlit app UI
st.set_page_config(page_title="PBTech Price Watcher", layout="centered")
st.title("📦 PBTech Price Drop Notifier")

# User input fields
url = st.text_input("🔗 Enter PBTech Product URL")
target_price = st.number_input("💰 Desired Price (NZD)", min_value=0.0, step=1.0)
phone_number = st.text_input("📱 Your Mobile Number (e.g., +6421xxxxxxx)")

# Load Twilio credentials from Streamlit secrets
try:
    sid = st.secrets["TWILIO_ACCOUNT_SID"]
    token = st.secrets["TWILIO_AUTH_TOKEN"]
    from_number = st.secrets["TWILIO_PHONE_NUMBER"]
except:
    st.error("🔐 Twilio credentials not found in secrets.")
    st.stop()

# Scraper function for PBTech product price
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
    except Exception as e:
        st.error(f"⚠️ Error while scraping: {e}")
    return None

# Run when the user clicks the button
if st.button("🔍 Check Now"):
    if not url or not phone_number:
        st.warning("Please fill in all fields.")
    else:
        price = get_pbtech_price(url)
        if price is not None:
            st.success(f"🛒 Current Price: ${price:,.2f}")
            if price <= target_price:
                client = Client(sid, token)
                body = f"📢 PBTech Deal: Price dropped to ${price}!\n{url}"
                client.messages.create(to=phone_number, from_=from_number, body=body)
                st.success("✅ SMS sent!")
            else:
                st.info("💤 Price is still above your target.")
        else:
            st.error("❌ Could not fetch price. Check the URL.")
