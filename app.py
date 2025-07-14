import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from twilio.rest import Client

# ------------------- Secrets -------------------
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    whatsapp_to = st.secrets["twilio"]["whatsapp_to"]
    openrouter_api_key = st.secrets["openrouter"]["api_key"]
except KeyError:
    st.error("❌ Missing credentials in `.streamlit/secrets.toml`.")
    st.stop()

whatsapp_from = "whatsapp:+14155238886"

# ------------------- UI -------------------
st.set_page_config(page_title="🦍 Price Watcher AI Advisor", layout="centered")
st.title("🧠 Smart Price Watcher with AI Advice & WhatsApp Alerts")

url = st.text_input("🔗 Product URL:", value="https://www.mightyape.co.nz/product/example-product/123456")
target_price = st.number_input("🎯 Target Price (NZD):", min_value=1.0, value=300.0)

# ------------------- Scraper -------------------
def get_price_and_comments(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
        )
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return None, []

        soup = BeautifulSoup(res.text, "html.parser")

        # Extract price
        price_element = soup.find("span", class_="buy-button-price")
        price = None
        if price_element:
            price = float(price_element.text.strip().replace("$", "").replace(",", ""))
        else:
            match = re.search(r"\$\d+(?:\.\d{2})?", soup.text)
            if match:
                price = float(match.group().replace("$", ""))

        # Simulate comment extraction
        comments = [tag.text.strip() for tag in soup.find_all("p", class_="review-content")]
        return price, comments[:5]

    except Exception as e:
        st.error(f"Scraper error: {e}")
        return None, []

# ------------------- AI Advisory -------------------
def generate_advice(comments):
    if not comments:
        return "🤖 No comments found to analyze."

    prompt = f"""
You're an AI shopping advisor. Based on the following product reviews, give a short sentiment summary and a BUY or DO NOT BUY recommendation with reason:

Reviews:
{chr(10).join(comments)}

Format:
Sentiment: ...
Recommendation: BUY/DO NOT BUY
Reason: ...
"""
    try:
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI error: {e}"

# ------------------- Main Logic -------------------
if st.button("🔍 Check Price & Send Alert"):
    if not url:
        st.warning("Please enter a product URL.")
    else:
        price, comments = get_price_and_comments(url)
        if price:
            st.success(f"✅ Current Price: ${price:.2f}")
            if comments:
                st.write("📝 Sample Comments Analyzed:")
                for c in comments:
                    st.markdown(f"- {c}")
            else:
                st.info("No comments available.")

            ai_advice = generate_advice(comments)
            st.markdown(f"💬 **AI Shopping Advice:**\n\n{ai_advice}")

            if price <= target_price:
                st.balloons()
                st.success("🎉 Price is below your target! Sending WhatsApp alert...")

                message_body = f"""🔥 Deal Alert!
Price: ${price:.2f}
Product: {url}

{ai_advice}"""

                try:
                    client = Client(twilio_sid, twilio_token)
                    client.messages.create(
                        body=message_body,
                        from_=whatsapp_from,
                        to=whatsapp_to
                    )
                    st.success("📲 WhatsApp message sent!")
                except Exception as sms_error:
                    st.error(f"WhatsApp error: {sms_error}")
            else:
                st.info("⏳ Price is still above your target.")
        else:
            st.error("❌ Price not found. Check the URL.")
