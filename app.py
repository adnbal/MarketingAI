import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from twilio.rest import Client

# ------------------- Twilio Config -------------------
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    whatsapp_to = st.secrets["twilio"]["whatsapp_to"]  # Format: whatsapp:+6421XXXXXXX
except KeyError:
    st.error("🔐 Missing Twilio credentials in `.streamlit/secrets.toml`.")
    st.stop()

whatsapp_from = "whatsapp:+14155238886"  # Twilio sandbox number

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="🦍 MightyApe Price Tracker", layout="centered")
st.title("🦍 MightyApe Price Watcher with WhatsApp Alerts")

url = st.text_input(
    "🔗 MightyApe product URL:",
    value="https://www.mightyape.co.nz/product/mighty-ape-heated-2-in-1-massager/35128615"
)

target_price = st.number_input("🎯 Target Price (NZD):", min_value=1.0, value=300.0)

# ------------------- Scraper Function -------------------
def get_mightyape_price(product_url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(product_url, headers=headers, timeout=10)
        if response.status_code == 403:
            st.error("❌ HTTP 403 Forbidden — the site may be blocking automated requests.")
            return None
        if response.status_code != 200:
            st.error(f"❌ HTTP error: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        price_element = soup.find("span", class_="buy-button-price")
        if price_element:
            price = price_element.text.strip().replace("$", "").replace(",", "")
            return float(price)

        # Fallback using regex
        match = re.search(r"\$\d+(?:\.\d{2})?", soup.text)
        if match:
            return float(match.group().replace("$", ""))
        return None
    except Exception as e:
        st.error(f"❌ Scraper error: {e}")
        return None

# ------------------- Main Logic -------------------
if st.button("🔍 Check Price"):
    if not url:
        st.warning("⚠️ Please enter the product URL.")
    else:
        price = get_mightyape_price(url)
        if price:
            st.success(f"✅ Current Price: ${price:,.2f}")
            if price <= target_price:
                st.balloons()
                st.success("🎉 Below your target! Sending WhatsApp alert...")

                client = Client(twilio_sid, twilio_token)
                try:
                    message = client.messages.create(
                        body=f"🔥 MightyApe Deal Alert!\nPrice: ${price:,.2f}\n{url}",
                        from_=whatsapp_from,
                        to=whatsapp_to
                    )
                    st.success("📲 WhatsApp message sent!")
                except Exception as sms_error:
                    st.error(f"📵 WhatsApp failed: {sms_error}")
            else:
                st.info("⏳ Price is still above your target.")
        else:
            st.error("❌ Could not extract price. Check the URL or site structure.")
