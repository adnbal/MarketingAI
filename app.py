import streamlit as st
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# --- UI ---
st.set_page_config(page_title="🦍 MightyApe Tracker", layout="centered")
st.title("🦍 MightyApe Price Watcher with Selenium (Cloud)")

url = st.text_input("🔗 Enter MightyApe product URL:")
target_price = st.number_input("🎯 Target Price (NZD):", min_value=1.0, value=100.0)

def scrape_price(url):
    try:
        options = Options()
        options.headless = True
        service = Service(executable_path="/usr/bin/geckodriver")  # Streamlit Cloud location
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        price_elem = soup.find("span", class_="buy-button-price")
        if price_elem:
            price = float(price_elem.text.replace("$", "").replace(",", "").strip())
        else:
            price = None

        title = soup.find("h1")
        return price, title.text.strip() if title else "Unknown Product"

    except Exception as e:
        st.error(f"❌ Selenium error: {e}")
        return None, None

if st.button("🔍 Check Price"):
    if not url:
        st.warning("⚠️ Enter a product URL.")
    else:
        price, title = scrape_price(url)
        if price:
            st.success(f"✅ {title}\n💰 Current Price: ${price:.2f}")
            if price <= target_price:
                st.balloons()
                st.success("🎉 Below your target! Consider buying now!")
            else:
                st.info("⏳ Still above your target.")
        else:
            st.error("❌ Could not extract price. Try again.")
