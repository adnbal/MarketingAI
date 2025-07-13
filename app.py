import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from twilio.rest import Client

# ------------------- Twilio Config -------------------
twilio_sid = st.secrets["twilio"]["account_sid"]
twilio_token = st.secrets["twilio"]["auth_token"]
twilio_from = st.secrets["twilio"]["from_number"]
twilio_to = st.text_input("📱 Your phone number to alert (e.g. +6421XXXXXXX)")

# ------------------- Streamlit UI -------------------
st.title("🦍 MightyApe Price Watcher with SMS Alerts")
url = st.text_input("🔗 Enter MightyApe product URL:")
target_price = st.number_input("🎯 Target Price ($):", min_value=1.0, value=100.0)

# ------------------- Scraper Function -------------------
def get_mightyape_price(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find first $ price using regex
        price_match = re.search(r"\$\d+(?:\.\d{2})?", soup.text)
        if price_match:
            return float(price_match.group().replace("$", ""))
        return None
    except Exception as e:
        print("Scraper error:", e)
        return None

# ------------------- Main Logic -------------------
if st.button("🔍 Check Price"):
    if url and twilio_to:
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
                st.warning("❌ Price is still higher than your target.")
        else:
            st.error("❌ Could not find price. Make sure the URL is from a product page.")
    else:
        st.error("⚠️ Please enter both a URL and your phone number.")
