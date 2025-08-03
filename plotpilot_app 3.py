
import streamlit as st
import requests

def geocode_postcode(postcode):
    url = f"https://api.postcodes.io/postcodes/{postcode}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 200:
            return data['result']['latitude'], data['result']['longitude']
    except requests.RequestException:
        return None, None
    return None, None

st.title("PlotPilot - AI Land Appraisal")

postcode = st.text_input("Enter a UK postcode:")

if postcode:
    lat, lon = geocode_postcode(postcode)
    if lat is None or lon is None:
        st.warning("Could not determine coordinates for the provided postcode.")
    else:
        st.success(f"Coordinates: Latitude {lat}, Longitude {lon}")
        # Placeholder for flood, greenbelt, topo, etc.
