import streamlit as st
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from textblob import TextBlob
from twilio.rest import Client

# ------------------- Twilio Config -------------------
try:
    twilio_sid = st.secrets["twilio"]["account_sid"]
    twilio_token = st.secrets["twilio"]["auth_token"]
    whatsapp_to = st.secrets["twilio"]["whatsapp_to"]
except KeyError:
    st.error("🔐 Twilio keys missing in `.streamlit/secrets.toml`.")
    st.stop()

whatsapp_from = "whatsapp:+14155238886"

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="🦍 MightyApe Deal Watcher", layout="centered")
st.title("🦍 MightyApe Price Alert + Smart Advice")

url = st.text_input(
    "🔗 MightyApe Product URL:",
    value="https://www.mightyape.co.nz/product/mighty-ape-heated-2-in-1-massager/35128615"
)
target_price = st.number_input("🎯 Target Price (NZD):", min_value=1.0, value=300.0)

# ------------------- Selenium Scraper -------------------
def get_product_info_selenium(url):
    options = Options()
    options.headless = True

    try:
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
        driver.get(url)
        st.info("🌐 Loading product page...")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        price_element = soup.find("span", class_="buy-button-price")
        if not price_element:
            return None, None, None

        price_text = price_element.text.strip().replace("$", "").replace(",", "")
        price = float(price_text)

        title = soup.find("h1").text.strip() if soup.find("h1") else "Unknown Product"
        desc = soup.find("div", class_="product-long-description")
        description = desc.get_text(strip=True) if desc else ""

        return price, title, description

    except Exception as e:
        st.error(f"❌ Selenium scraper error: {e}")
        return None, None, None

# ------------------- Sentiment & Ranking -------------------
def analyze_sentiment(text):
    if not text:
        return 0.0, "Neutral"
    blob = TextBlob(text)
    score = blob.sentiment.polarity
    label = "Positive" if score > 0.2 else "Negative" if score < -0.2 else "Neutral"
    return round(score * 100, 1), label

def calculate_rank(price, target_price, sentiment_score):
    price_delta = max(0, min(100, int(((target_price - price) / target_price) * 100)))
    rank = int((0.6 * price_delta) + (0.4 * sentiment_score))
    return min(rank, 100)

# ------------------- Main Logic -------------------
if st.button("🔍 Check Price"):
    if not url:
        st.warning("⚠️ Please enter a valid product URL.")
    else:
        price, title, description = get_product_info_selenium(url)
        sentiment_score, sentiment_label = analyze_sentiment(description)

        if price is not None:
            price_delta = target_price - price
            rank_score = calculate_rank(price, target_price, sentiment_score)

            st.success(f"✅ Price: ${price:,.2f}")
            st.markdown(f"💬 **Sentiment:** {sentiment_label} ({sentiment_score}%)")
            st.markdown(f"📊 **Ranking Score:** {rank_score}/100")
            st.markdown(f"🎯 **Savings:** ${price_delta:,.2f}")

            advice = "✅ Buy now!" if rank_score >= 70 else "🤔 Wait or check reviews."

            if price <= target_price:
                st.balloons()
                st.success("🎉 Below target — sending WhatsApp alert...")

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
                st.info("⏳ Price is above your target.")
        else:
            st.error("❌ Could not extract product data.")
