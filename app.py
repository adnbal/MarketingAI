import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from twilio.rest import Client

# ------------------- Twilio Config -------------------
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    twilio_from = st.secrets["twilio"]["from_number"]
except KeyError:
    st.error("🔐 Twilio credentials not found in `.streamlit/secrets.toml`.")
    st.stop()

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="🦍 MightyApe Price Tracker", layout="centered")
st.title("🦍 MightyApe Price Watcher with SMS Alerts")
url = st.text_input("🔗 Enter MightyApe product URL:")
target_price = st.number_input("🎯 Target Price (NZD):", min_value=1.0, value=100.0)
twilio_to = st.text_input("📱 Your mobile number (e.g. +6421XXXXXXX)")

# ------------------- Scraper Function -------------------
def get_mightyape_price(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            st.error(f"❌ HTTP error: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try specific price class
        price_element = soup.find("span", class_="buy-button-price")
        if price_element:
            price_text = price_element.text.strip().replace("$", "").replace(",", "")
            return float(price_text)

        # Fallback: try regex
        match = re.search(r"\$\d+(?:\.\d{2})?", soup.text)
        if match:
            return float(match.group().replace("$", ""))

        return None
    except Exception as e:
        st.error(f"❌ Scraper error: {e}")
        return None

# ------------------- Main Logic -------------------
if st.button("🔍 Check Price"):
    if not url or not twilio_to:
        st.warning("⚠️ Please enter both the product URL and your phone number.")
    else:
        price = get_mightyape_price(url)
        if price:
            st.success(f"✅ Current Price: ${price:,.2f}")
            if price <= target_price:
                st.balloons()
                st.success("🎉 Below your target! Sending SMS...")
                client = Client(twilio_sid, twilio_token)
                try:
                    client.messages.create(
                        body=f"🔥 MightyApe Deal Alert!\nPrice: ${price:,.2f}\n{url}",
                        from_=twilio_from,
                        to=twilio_to
                    )
                except Exception as sms_error:
                    st.error(f"📵 SMS failed: {sms_error}")
            else:
                st.info("⏳ Price is still above your target.")
        else:
            st.error("❌ Could not find price. Make sure the URL is from a valid product page.")
