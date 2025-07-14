import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from textblob import TextBlob
from twilio.rest import Client

# ------------------- Twilio Config -------------------
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    whatsapp_to = st.secrets["twilio"]["whatsapp_to"]
except KeyError:
    st.error("❌ Missing Twilio credentials in `.streamlit/secrets.toml`.")
    st.stop()

whatsapp_from = "whatsapp:+14155238886"  # Twilio Sandbox number

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="🦍 NZ Price Watcher", layout="centered")
st.title("🛍️ Smart NZ Price Tracker + Sentiment Advice")

url = st.text_input("🔗 Product URL:", value="https://www.mightyape.co.nz/product/example")
target_price = st.number_input("🎯 Target Price (NZD):", min_value=1.0, value=300.0)

# ------------------- Price Extractor -------------------
def extract_price_from_soup(soup):
    try:
        price_element = soup.find("span", class_="buy-button-price")
        if price_element:
            return float(price_element.text.strip().replace("$", "").replace(",", ""))
        meta_price = soup.find("meta", property="product:price:amount")
        if meta_price:
            return float(meta_price["content"])
        match = re.search(r"\$\d+(?:\.\d{2})?", soup.text)
        if match:
            return float(match.group().replace("$", ""))
    except:
        return None
    return None

# ------------------- Review Sentiment (Dummy) -------------------
def dummy_sentiment_analysis(text):
    if "good" in text.lower() or "love" in text.lower():
        return "Positive", "👍 Customers love it! Worth considering."
    elif "bad" in text.lower() or "poor" in text.lower():
        return "Negative", "👎 Many users report issues. Be cautious."
    else:
        return "Neutral", "😐 Mixed feedback. Read more before buying."

# ------------------- Scraper -------------------
def get_product_info(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            st.error(f"❌ HTTP error: {res.status_code}")
            return None, None

        soup = BeautifulSoup(res.text, "html.parser")
        price = extract_price_from_soup(soup)

        # Dummy review extraction (real sites need auth or API)
        sample_comment = "Great product and works really well!"  # Replace with actual scraping if allowed
        sentiment, advice = dummy_sentiment_analysis(sample_comment)
        return price, advice
    except Exception as e:
        st.error(f"❌ Scraper error: {e}")
        return None, None

# ------------------- Main Logic -------------------
if st.button("🔍 Check Price & Advice"):
    if not url:
        st.warning("⚠️ Please enter a valid product URL.")
    else:
        price, advice = get_product_info(url)
        if price is not None:
            st.success(f"✅ Current Price: ${price:,.2f}")
            st.info(f"💬 AI Sentiment Advice: {advice}")
            if price <= target_price:
                st.balloons()
                st.success("🎉 Price dropped below your target! Sending WhatsApp alert...")

                client = Client(twilio_sid, twilio_token)
                try:
                    message = client.messages.create(
                        body=f"🔥 Deal Alert!\nPrice: ${price:,.2f}\nAdvice: {advice}\n{url}",
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
