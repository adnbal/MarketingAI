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

url = st.text_input(
    "🔗 MightyApe product URL:",
    value="https://www.mightyape.co.nz/mn/buy/mighty-ape-ape-basics-heated-2-in-1-shiatsu-foot-and-back-massager-35128615/"
)
target_price = st.number_input("🎯 Target Price (NZD):", min_value=1.0, value=300.0)
twilio_to = st.text_input("📱 Your mobile number (e.g. +6421XXXXXXX)")

# ------------------- Scraper Function -------------------
def get_mightyape_price(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }
    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code != 200:
        st.error(f"❌ HTTP error: {res.status_code}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")

    # Extract price from button span
    span = soup.find("span", class_="buy-button-price")
    if span:
        txt = span.get_text(strip=True).replace("$", "").replace(",", "")
        return float(txt)

    # Fallback regex
    m = re.search(r"\$\d+(?:\.\d{2})?", soup.text)
    if m:
        return float(m.group().replace("$", ""))

    st.error("⚠️ Price element not found; site structure may have changed.")
    return None

# ------------------- Main Logic -------------------
if st.button("🔍 Check Price"):
    if not url or not twilio_to:
        st.warning("⚠️ Please enter both URL and your phone number.")
    else:
        price = get_mightyape_price(url)
        if price is not None:
            st.success(f"✅ Current Price: ${price:,.2f}")
            if price <= target_price:
                st.balloons()
                st.success("🎉 Below your target! Sending SMS...")
                client = Client(twilio_sid, twilio_token)
                try:
                    client.messages.create(
                        body=f"🔥 Deal! Price is ${price:,.2f}\n{url}",
                        from_=twilio_from,
                        to=twilio_to
                    )
                    st.success("📲 SMS sent!")
                except Exception as e:
                    st.error(f"📵 SMS failed: {e}")
            else:
                st.info("⏳ Price still above your target.")
