import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from twilio.rest import Client
from textblob import TextBlob

# --- Setup ---
st.set_page_config(page_title="🦍 Price Tracker + AI Advice", layout="centered")
st.title("🦍 Smart Price Watcher with WhatsApp + AI Advice")

# --- Secret Config ---
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    whatsapp_to = st.secrets["twilio"]["whatsapp_to"]
    whatsapp_from = "whatsapp:+14155238886"

    gemini_key = st.secrets["gemini"]["api_key"]
    openrouter_key = st.secrets["openrouter"]["api_key"]
except KeyError:
    st.error("❌ Missing credentials in Streamlit secrets.")
    st.stop()

# --- Inputs ---
url = st.text_input("🔗 MightyApe Product URL", 
    value="https://www.mightyape.co.nz/product/apple-airpods-pro-2nd-generation-usb-c/38224439")
target_price = st.number_input("🎯 Target Price (NZD)", min_value=1.0, value=300.0)

# --- Scraper Helper ---
def extract_price_from_soup(soup):
    try:
        span_price = soup.find("span", class_="buy-button-price")
        if span_price:
            return float(span_price.text.strip().replace("$", "").replace(",", ""))
        meta_price = soup.find("meta", property="product:price:amount")
        if meta_price:
            return float(meta_price["content"])
        match = re.search(r"\$\d+(?:\.\d{2})?", soup.text)
        if match:
            return float(match.group().replace("$", ""))
    except:
        return None
    return None

def extract_reviews(soup):
    reviews = soup.find_all("div", class_="product-review-body")
    if not reviews:
        return "No reviews found."
    return " ".join([r.text.strip() for r in reviews[:5]])

# --- AI Sentiment & Advice ---
def get_sentiment_advice(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.3:
        return f"🟢 Positive sentiment. Recommended to buy.\nReason: Users seem happy with the product."
    elif polarity < -0.3:
        return f"🔴 Negative sentiment. Not recommended.\nReason: Many concerns or issues raised."
    else:
        return f"🟡 Neutral sentiment. Consider checking more reviews."

# --- Main Logic ---
if st.button("🔍 Check Price and Send Advice"):
    with st.spinner("Fetching product info..."):
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200:
                st.error(f"❌ HTTP error: {res.status_code}")
                st.stop()
            soup = BeautifulSoup(res.text, "html.parser")
            price = extract_price_from_soup(soup)
            if not price:
                st.error("❌ Price not found. Check the URL or site structure.")
                st.stop()

            st.success(f"✅ Current Price: ${price:.2f}")
            reviews_text = extract_reviews(soup)
            sentiment = get_sentiment_advice(reviews_text)

            # WhatsApp Alert
            body_msg = (
                f"🦍 Deal Alert!\n"
                f"Price: ${price:.2f}\n"
                f"{sentiment}\n"
                f"🔗 {url}"
            )
            if price <= target_price:
                client = Client(twilio_sid, twilio_token)
                client.messages.create(body=body_msg, from_=whatsapp_from, to=whatsapp_to)
                st.balloons()
                st.success("📲 WhatsApp Alert Sent with Sentiment Advice!")
            else:
                st.info("⏳ Still above target price.")
                st.write(sentiment)

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
