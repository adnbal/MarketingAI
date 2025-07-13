import streamlit as st
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from webdriver_manager.firefox import GeckoDriverManager

# --- App config ---
st.set_page_config(page_title="🦍 MightyApe Price Tracker", layout="centered")
st.title("🦍 MightyApe Price Watcher with Selenium")

# --- User Input ---
url = st.text_input("🔗 Enter MightyApe product URL:")
target_price = st.number_input("🎯 Target Price (NZD):", min_value=1.0, value=100.0)

# --- Scraper using Selenium ---
def get_product_info_selenium(url):
    options = Options()
    options.headless = True

    # ✅ Set Firefox binary path for Windows (your system)
    binary_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
    binary = FirefoxBinary(binary_path)
    options.binary = binary

    try:
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        # Extract product price
        price_element = soup.find("span", class_="buy-button-price")
        if price_element:
            price_text = price_element.text.strip().replace("$", "").replace(",", "")
            price = float(price_text)
        else:
            price = None

        # Extract product title
        title_element = soup.find("h1")
        title = title_element.text.strip() if title_element else "Unknown Product"

        return price, title

    except Exception as e:
        st.error(f"❌ Selenium scraper error: {e}")
        return None, None

# --- Main logic ---
if st.button("🔍 Check Price"):
    if not url:
        st.warning("⚠️ Please enter the product URL.")
    else:
        price, title = get_product_info_selenium(url)
        if price:
            st.success(f"✅ {title}\n💰 Current Price: ${price:.2f}")
            if price <= target_price:
                st.balloons()
                st.success("🎉 Below your target! Consider buying now!")
            else:
                st.info("⏳ Price is still above your target.")
        else:
            st.error("❌ Could not extract product data. Check the URL or try again.")
