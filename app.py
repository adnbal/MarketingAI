import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from twilio.rest import Client

# --- Twilio Config ---
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    twilio_from = st.secrets["twilio"]["from_number"]
except KeyError:
    st.error("🔐 Twilio credentials not found in .streamlit/secrets.toml")
    st.stop()

# --- Streamlit UI ---
st.title("🦍 MightyApe Price Watcher with SMS Alerts")
url = st.text_input("🔗 Enter MightyApe product URL:")
target_price = st.number_input("🎯 Target Price ($):", min_value=1.0, value=100.0)
twilio_to = st.text_input("📱 Your phone number (e.g. +6421XXXXXXX)")

# --- Price Scraper Function ---
def get_mightyape_price(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Try structured span first
        price_span = soup.find("span", class_="buy-button-price")
        if price_span:
            price_text = price_span.get_text(strip=True)
            return float(price_text.replace("$", "").replace(",", ""))

        # Fallback to regex
        price_match = re.search(r"\$\d+(?:\.\d{2})?", soup.text)
        if price_match:
            return float(price_match.group().replace("$", ""))

        return None
    except Exception as e:
        print("Scraper error:", e)
        return None

# --- Main Action ---
if st.button("🔍 Check Price"):
    if not url or not twilio_to:
        st.error("Please enter both the product URL and your phone number.")
    else:
        price = get_mightyape_price(url)
        if price:
            st.success(f"✅ Current Price: ${price:,.2f}")
            if price <= target_price:
                st.balloons()
                st.success("🎉 Price is below your target! Sending SMS...")
                client = Client(twilio_sid, twilio_token)
                client.messages.create(
                    body=f"🔥 MightyApe Deal Alert!\nPrice: ${price:,.2f}\n{url}",
                    from_=twilio_from,
                    to=twilio_to
                )
            else:
                st.warning("❌ Price is still above your target.")
        else:
            st.error("❌ Could not find price. Make sure the URL is from a product page.")
