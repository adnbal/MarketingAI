import streamlit as st
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
from webdriver_manager.firefox import GeckoDriverManager

st.set_page_config(page_title="🦍 MightyApe Price Watcher", layout="centered")
st.title("🦍 MightyApe Price Tracker")

url = st.text_input("🔗 Product URL")
target_price = st.number_input("🎯 Target Price (NZD)", min_value=1.0, value=100.0)

def scrape_price(url):
    try:
        options = Options()
        options.headless = True
        service = Service("/usr/bin/geckodriver")
        driver = webdriver.Firefox(service=service, options=options)

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        price_tag = soup.find("span", class_="buy-button-price")
        title_tag = soup.find("h1")

        price = float(price_tag.text.replace("$", "").strip()) if price_tag else None
        title = title_tag.text.strip() if title_tag else "Unknown Product"
        return price, title

    except Exception as e:
        st.error(f"❌ Selenium scraper error: {e}")
        return None, None

if st.button("🔍 Check Price"):
    if not url:
        st.warning("Please enter a product URL.")
    else:
        price, title = scrape_price(url)
        if price:
            st.success(f"🛒 {title}\n💰 Current Price: ${price}")
            if price <= target_price:
                st.balloons()
                st.success("🎉 Price is below target!")
            else:
                st.info("💤 Still above your target.")
        else:
            st.error("❌ Could not extract price.")
