import streamlit as st
from scraper import get_price_noel_leeming

st.title("🛒 NZ Price Watcher")

url = st.text_input("Paste Noel Leeming product URL:")
target_price = st.number_input("Notify if price drops below (NZD)", min_value=1.0, step=1.0)

if st.button("Check Now"):
    current_price = get_price_noel_leeming(url)
    
    if current_price:
        st.write(f"🔎 Current Price: ${current_price:,.2f}")
        if current_price <= target_price:
            st.success("✅ Great! Price has dropped below your target!")
        else:
            st.info("ℹ️ Not yet. Keep watching...")
    else:
        st.error("❌ Couldn't fetch price. Check the URL or site layout.")
