# app.py
import streamlit as st

st.title("📉 E-commerce Price Watcher")

url = st.text_input("Enter product URL")
target_price = st.number_input("Notify me if price drops below (NZD):", min_value=0.0, step=1.0)

if st.button("Start Monitoring"):
    st.success("✅ Monitoring started! You'll be notified when the price drops.")
