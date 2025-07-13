def get_pbtech_price(url):
    import requests
    from bs4 import BeautifulSoup

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # NEW: Find the price div with data-price attribute
        price_div = soup.find("div", {"data-price": True})
        if price_div:
            return float(price_div["data-price"])

        # FALLBACK: Try old span.price (for older listings)
        price_span = soup.find("span", class_="price")
        if price_span:
            return float(price_span.text.replace("$", "").replace(",", "").strip())

    except Exception as e:
        print(f"Scraper error: {e}")
        return None

    return None
