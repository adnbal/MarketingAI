import streamlit as st
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

# --- Streamlit UI ---
st.set_page_config(page_title="🐵 MightyApe Price Watch", layout="centered")
st.title("📦 MightyApe Price Tracker with SMS Alert")

url = st.text_input("🔗 Paste a MightyApe Product URL:")
target_price = st.number_input("🎯 Your Target Price (NZD):", min_value=1.0, value=100.0)
user_phone = st.text_input("📱 Your Mobile Number (e.g., +6421XXXXXXX)")

# --- Twilio Secrets (from Streamlit Cloud)
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    twilio_from = st.secrets["twilio"]["from_number"]
except Exception as e:
    st.warning("🔐 Twilio credentials not found in `.streamlit/secrets.toml`")

# --- Scrape MightyApe Price ---
def get_mightyape_price(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Find span with class 'price' or 'our-price'
        price_el = soup.find("span", class_="price")
        if not price_el:
            price_el = soup.find("span", class_="our-price")
        if not price_el:
            return None

        price_text = price_el.text.strip().replace("$", "").replace(",", "")
        return float(price_text)
    except Exception as e:
        st.error(f"❌ Error while scraping price: {e}")
        return None

# --- Main Execution ---
if st.button("🔍 Check Price"):
    if url and user_phone:
        price = get_mightyape_price(url)
        if price is not None:
            st.success(f"✅ Current Price: ${price:,.2f}")
            if price <= target_price:
                st.success("🎉 Below target price! Sending SMS...")
                try:
                    client = Client(twilio_sid, twilio_token)
                    client.messages.create(
                        body=f"🔥 MightyApe Deal Alert!\nPrice: ${price:,.2f}\n{url}",
                        from_=twilio_from,
                        to=user_phone
                    )
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ SMS failed: {e}")
            else:
                st.info("⏳ Price is still above your target.")
        else:
            st.error("❌ Could not find price. Make sure the URL is from a product page.")
    else:
        st.warning("⚠️ Please enter both a product URL and your phone number.")
