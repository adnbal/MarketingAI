import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from twilio.rest import Client

# ------------------- Twilio Config -------------------
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    whatsapp_to = st.secrets["twilio"]["whatsapp_to"]
except KeyError:
    st.error("🔐 Missing Twilio credentials in `.streamlit/secrets.toml`.")
    st.stop()

whatsapp_from = "whatsapp:+14155238886"  # Twilio Sandbox

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="🦍 Price Tracker with AI Advice", layout="centered")
st.title("🦍 Price Watcher + AI Advice via WhatsApp")

url = st.text_input("🔗 Product URL (MightyApe):", 
                    value="https://www.mightyape.co.nz/product/playstation-5-console/34510783")

target_price = st.number_input("🎯 Target Price (NZD):", min_value=1.0, value=800.0)

# ------------------- Price Scraper -------------------
def get_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 403:
            st.error("❌ HTTP 403 Forbidden: MightyApe may be blocking the scraper.")
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        price_element = soup.find("span", class_="buy-button-price")
        if price_element:
            price_text = price_element.text.strip().replace("$", "").replace(",", "")
            return float(price_text)

        match = re.search(r"\$\d+(?:\.\d{2})?", soup.text)
        if match:
            return float(match.group().replace("$", ""))
        return None
    except Exception as e:
        st.error(f"❌ Scraper error: {e}")
        return None

# ------------------- Dummy Sentiment Advice -------------------
def dummy_sentiment_advice(price, target_price):
    if price <= target_price:
        return "👍 Great deal! Customers seem happy and price is within your range."
    elif price <= target_price * 1.1:
        return "🤔 Almost there. Maybe wait a bit longer or look at recent reviews."
    else:
        return "❌ Too expensive right now. Hold off unless urgent."

# ------------------- Main Logic -------------------
if st.button("🔍 Check Price"):
    if not url:
        st.warning("⚠️ Please enter a valid product URL.")
    else:
        price = get_price(url)
        if price is not None:
            st.success(f"✅ Current Price: ${price:,.2f}")
            advice = dummy_sentiment_advice(price, target_price)
            st.info(advice)

            if price <= target_price:
                st.balloons()
                st.success("🎉 Price is below target. Sending WhatsApp alert...")

                message_body = (
                    f"🔥 MightyApe Deal Alert!\n\n"
                    f"Product: {url}\n"
                    f"Current Price: ${price:,.2f}\n"
                    f"AI Advice: {advice}"
                )

                try:
                    client = Client(twilio_sid, twilio_token)
                    client.messages.create(
                        body=message_body,
                        from_=whatsapp_from,
                        to=whatsapp_to
                    )
                    st.success("📲 WhatsApp message sent!")
                except Exception as sms_error:
                    st.error(f"📵 WhatsApp failed: {sms_error}")
            else:
                st.info("⏳ Still above your target. No alert sent.")
        else:
            st.error("❌ Could not extract price. Check the URL or try later.")
