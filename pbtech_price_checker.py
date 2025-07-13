from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

def get_pbtech_price(url):
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)

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
