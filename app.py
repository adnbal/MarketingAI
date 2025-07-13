import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client

# --- Streamlit Page Setup ---
st.set_page_config(page_title="PBTech Price Watcher", layout="centered")
st.title("📦 PBTech Price Drop Notifier")

# --- User Input ---
url = st.text_input("🔗 Enter PBTech Product URL")
target_price = st.number_input("💰 Desired Price (NZD)", min_value=0.0, step=1.0)
phone_number = st.text_input("📱 Your Mobile Number (e.g., +6421xxxxxxx)")

# --- Twilio Setup (stored in .streamlit/secrets.toml) ---
try:
    sid = st.secrets["TWILIO_ACCOUNT_SID"]
    token = st.secrets["TWILIO_AUTH_TOKEN"]
    from_number = st.secrets["TWILIO_PHONE_NUMBER"]
except Exception:
    st.error("🔐 Twilio credentials not found in Streamlit secrets.")
    st.stop()

# --- Selenium Price Scraper ---
def get_pbtech_price(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    try:
        driver.get(url)
        price_elem = driver.find_element("css selector", "span.price")
        price_text = price_elem.text.strip().replace("$", "").replace(",", "")
        return float(price_text)
    except Exception as e:
        print("Scraping error:", e)
        return None
    finally:
        driver.quit()

# --- App Logic ---
if st.button("🔍 Check Price Now"):
    if not url or not phone_number:
        st.warning("⚠️ Please fill in all fields.")
    else:
        st.write("🔎 Fetching price from PBTech...")
        price = get_pbtech_price(url)
        if price is not None:
            st.success(f"🛒 Current Price: ${price:,.2f}")
            if price <= target_price:
                client = Client(sid, token)
                message = f"📢 Deal Alert: PBTech price dropped to ${price:,.2f}!\n{url}"
                client.messages.create(to=phone_number, from_=from_number, body=message)
                st.success("✅ SMS alert sent!")
            else:
                st.info("💤 Price is still above your target.")
        else:
            st.error("❌ Could not fetch price. Check the URL or try another product.")
