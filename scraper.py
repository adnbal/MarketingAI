def get_pbtech_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    # PBTech uses span.price on product pages
    price_span = soup.select_one("span.price")

    if price_span:
        try:
            price_str = price_span.text.replace("$", "").replace(",", "").strip()
            return float(price_str)
        except:
            return None
    return None
