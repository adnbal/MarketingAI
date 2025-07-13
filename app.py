import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from twilio.rest import Client
from textblob import TextBlob

# ------------------- Twilio Config -------------------
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    whatsapp_to = st.secrets["twilio"]["whatsapp_to"]
except KeyError:
    st.error("🔐 Missing Twilio credentials in `.streamlit/secrets.toml`.")
    st.stop()

whatsapp_from = "whatsapp:+14155238886"  # Twilio sandbox number

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="🦍 MightyApe Smart Deal Advisor", layout="centered")
st.title("🦍 MightyApe Price Watcher + Sentiment & Smart Ranking")

url = st.text_input(
    "🔗 MightyApe product URL:",
    value="https://www.mightyape.co.nz/mn/buy/mighty-ape-ape-basics-heated-2-in-1-shiatsu-foot-and-back-massager-35128615/"
)
target_price = st.number_input("🎯 Target Price (NZD):", min_value=1.0, value=300.0)

# ------------------- Scraper + Sentiment -------------------
def get_product_info(url):
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    })

    try:
        res = session.get(url, timeout=10)
        if res.status_code != 200:
            st.error(f"❌ HTTP error: {res.status_code}")
            return None, None, None

        soup = BeautifulSoup(res.text, "html.parser")

        price_element = soup.find("span", class_="buy-button-price")
        price = None
        if price_element:
            price_text = price_element.text.strip().replace("$", "").replace(",", "")
            price = float(price_text)

        title = soup.find("h1").text.strip() if soup.find("h1") else "Unknown Product"

        desc = soup.find("div", class_="product-long-description")
        description = desc.get_text(strip=True) if desc else ""

        return price, title, description
    except Exception as e:
        st.error(f"❌ Scraper error: {e}")
        return None, None, None

def analyze_sentiment(text):
    if not text:
        return 0.0, "Neutral"
    blob = TextBlob(text)
    score = blob.sentiment.polarity
    label = "Positive" if score > 0.2 else "Negative" if score < -0.2 else "Neutral"
    return round(score * 100, 1), label

def calculate_rank(price, target_price, sentiment_score):
    if not price or not target_price:
        return 0
    price_delta = max(0, min(100, int(((target_price - price) / target_price) * 100)))
    rank = int((0.6 * price_delta) + (0.4 * sentiment_score))
    return min(rank, 100)

# ------------------- Main Logic -------------------
if st.button("🔍 Check Price"):
    if not url:
        st.warning("⚠️ Please enter the product URL.")
    else:
        price, title, description = get_product_info(url)
        sentiment_score, sentiment_label = analyze_sentiment(description)

        if price is not None:
            price_delta = target_price - price
            rank_score = calculate_rank(price, target_price, sentiment_score)

            st.success(f"✅ Current Price: ${price:,.2f}")
            st.markdown(f"💬 **Sentiment:** {sentiment_label} ({sentiment_score}%)")
            st.markdown(f"📊 **Ranking Score:** {rank_score}/100")
            st.markdown(f"🎯 **You Save:** ${price_delta:,.2f}")

            advice = "✅ Recommended to buy now!" if rank_score >= 70 else "🤔 Wait or check reviews."

            if price <= target_price:
                st.balloons()
                st.success("🎉 Below your target! Sending WhatsApp alert...")

                client = Client(twilio_sid, twilio_token)
                try:
                    message = client.messages.create(
                        body=(
                            f"🔥 MightyApe Deal Alert!\n\n"
                            f"🛍️ {title}\n"
                            f"💲 Price: ${price:.2f} (Target: ${target_price:.2f})\n"
                            f"💬 Sentiment: {sentiment_label} ({sentiment_score}%)\n"
                            f"📊 Ranking Score: {rank_score}/100\n"
                            f"🤖 Advice: {advice}\n"
                            f"🔗 {url}"
                        ),
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
