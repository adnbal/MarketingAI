import streamlit as st
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

# --- Page Config ---
st.set_page_config(page_title="📦 TheMarket Price Watcher", layout="centered")
st.title("🛒 TheMarket NZ Price Watcher with SMS Alert")

# --- User Inputs ---
url = st.text_input("🔗 Paste a TheMarket product URL:")
target_price = st.number_input("🎯 Your Target Price (NZD):", min_value=1.0, value=100.0)
user_phone = st.text_input("📱 Your Mobile Number (e.g., +6421XXXXXXX)")

# --- Twilio Config ---
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    twilio_from = st.secrets["twilio"]["from_number"]
except:
    st.warning("🔐 Twilio credentials not found in `.streamlit/secrets.toml`")

# --- Price Scraper ---
def get_market_price(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        price_span = soup.find("span", {"data-testid": "product-price"})

        if not price_span:
            return None

        price_text = price_span.text.strip().replace("$", "").replace(",", "")
        return float(price_text)
    except Exception as e:
        st.error(f"❌ Error scraping price: {e}")
        return None

# --- Main Action ---
if st.button("🔍 Check Price"):
    if url and user_phone:
        price = get_market_price(url)
        if price is not None:
            st.success(f"✅ Current Price: ${price:,.2f}")
            if price <= target_price:
                st.success("🎉 Price is below your target! Sending SMS...")
                try:
                    client = Client(twilio_sid, twilio_token)
                    client.messages.create(
                        body=f"🔥 Deal Alert on TheMarket!\nPrice: ${price:,.2f}\n{url}",
                        from_=twilio_from,
                        to=user_phone
                    )
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ SMS failed: {e}")
            else:
                st.info("⏳ Price is still above your target.")
        else:
            st.error("❌ Could not find price. Make sure the URL is a valid TheMarket product page.")
    else:
        st.warning("⚠️ Please enter both a valid URL and phone number.")
