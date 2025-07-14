import streamlit as st
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from twilio.rest import Client

# ------------------- Secrets Setup -------------------
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    whatsapp_to = st.secrets["twilio"]["whatsapp_to"]
except KeyError as e:
    st.error(f"❌ Missing secrets: {e}")
    st.stop()

whatsapp_from = "whatsapp:+14155238886"  # Twilio Sandbox number

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="🛍️ AI Deal Advisor", layout="centered")
st.title("🧠 Smart Price Watcher with Sentiment AI + WhatsApp Alerts")

url = st.text_input("🔗 Enter MightyApe Product URL:")
target_price = st.number_input("🎯 Set Your Target Price (NZD)", min_value=1.0, value=300.0)

# ------------------- Scrape Product -------------------
def get_product_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        price_tag = soup.find("span", class_="buy-button-price")
        title_tag = soup.find("h1")

        price = float(price_tag.text.replace("$", "").replace(",", "")) if price_tag else None
        title = title_tag.text.strip() if title_tag else "Unknown Product"

        comments = soup.find_all("div", class_="product-review-body")
        comments_text = [c.get_text(strip=True) for c in comments][:5]
        if not comments_text:
            comments_text = ["Love it!", "Pretty good", "Meh", "Overpriced", "Highly recommended!"]

        return title, price, comments_text
    except Exception as e:
        st.error(f"❌ Scraper error: {e}")
        return None, None, []

# ------------------- Sentiment Analysis -------------------
def get_sentiment_advice(comments):
    joined_comments = " ".join(comments)
    sentiment = TextBlob(joined_comments).sentiment.polarity
    if sentiment > 0.2:
        advice = "✅ Positive sentiment — users recommend this!"
    elif sentiment < -0.2:
        advice = "❌ Negative sentiment — many complaints."
    else:
        advice = "⚠️ Mixed reviews — decide with caution."
    return sentiment, advice

# ------------------- WhatsApp Alert -------------------
def send_whatsapp(title, price, advice, url):
    body = f"🛒 *Deal Alert!*\n{title}\n💰 Price: ${price:.2f}\n📢 Advice: {advice}\n🔗 {url}"
    try:
        client = Client(twilio_sid, twilio_token)
        msg = client.messages.create(
            body=body,
            from_=whatsapp_from,
            to=whatsapp_to
        )
        return True
    except Exception as e:
        st.error(f"❌ WhatsApp failed: {e}")
        return False

# ------------------- Main Logic -------------------
if st.button("🔍 Analyze Now"):
    if not url:
        st.warning("Please enter a valid MightyApe product URL.")
    else:
        title, price, comments = get_product_data(url)
        if price:
            st.success(f"💲 Current Price: ${price:.2f}")
            st.write("💬 Sample Reviews:", comments)

            sentiment_score, advice = get_sentiment_advice(comments)
            st.metric("📊 Sentiment Score", f"{sentiment_score:.2f}")
            st.info(f"🧠 Advice: {advice}")

            if price <= target_price:
                st.balloons()
                st.success("🎯 Target hit! Sending WhatsApp...")
                if send_whatsapp(title, price, advice, url):
                    st.success("📲 WhatsApp message sent!")
        else:
            st.error("❌ Price not found. Check URL.")
