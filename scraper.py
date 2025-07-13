import requests
from bs4 import BeautifulSoup

def get_price_noel_leeming(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    # 🎯 Extract price (Noel Leeming uses this class for price)
    price_element = soup.select_one(".price-box .price")
    
    if price_element:
        price_str = price_element.text.strip().replace("$", "").replace(",", "")
        try:
            return float(price_str)
        except:
            return None
    return None
