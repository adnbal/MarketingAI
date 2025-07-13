import streamlit as st
from twilio.rest import Client
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="💰 PBTech Price Notifier", layout="centered")
st.title("🛒 PBTech Price Drop Watcher")

# --- Input Form ---
url = st.text_input("📦 Enter PBTech product URL")
target_price = st.number_input("💸 Desired price (NZD):", min_value=0.0, step=1.0)
phone_number = st.text_input("📱 Your NZ mobile number (e.g., +6421xxxxxxx)")

# --- Get secrets from Streamlit Cloud or local .streamlit/secrets.toml ---
try:
    sid = st.secrets["TWILIO_ACCOUNT_SID"]
    token = st.secrets["TWILIO_AUTH_TOKEN"]
    from_number = st.secrets["TWILIO_PHONE_NUMBER"]
except:
    st.error("❌ Twilio credentials not found. Add them to Streamlit Secrets.")
    st.stop()

# --- Price scraper ---
def get_pbtech_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    price_tag = soup.select_one("meta[itemprop='price']")
    return float(price_tag['content']) if price_tag else None

# --- Trigger ---
if st.button("🔍 Check Price and Notify"):
    if not url or not phone_number:
        st.warning("Please fill in all fields.")
    else:
        price = get_pbtech_price(url)
        if price:
            st.write(f"💵 Current Price: ${price:,.2f}")
            if price <= target_price:
                client = Client(sid, token)
                body = f"📢 Price Alert! PBTech item dropped to ${price}!\n{url}"
                client.messages.create(to=phone_number, from_=from_number, body=body)
                st.success("✅ SMS sent! Price matched your target.")
            else:
                st.info("ℹ️ Price is still above your target. No SMS sent.")
        else:
            st.error("❌ Could not fetch price. Check the URL.")
