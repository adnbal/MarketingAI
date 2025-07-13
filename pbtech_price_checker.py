from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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
