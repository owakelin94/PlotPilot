
import streamlit as st
import requests

st.set_page_config(page_title="PlotPilot – AI Land Appraisal")
st.title("PlotPilot")
st.subheader("AI Land Appraisal")

# Input
postcode = st.text_input("Enter postcode:")

# Initialise outputs
flood_result = "Not available"
greenbelt_result = "Not available"
elevation_result = "Not available"
utility_result = "Not available"
lat = lon = None

# Functions
def geocode_postcode(postcode):
    url = f"https://api.postcodes.io/postcodes/{postcode}"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        return data['result']['latitude'], data['result']['longitude']
    except:
        return None, None

def get_flood_zone(lat, lon):
    try:
        url = f"https://environment.data.gov.uk/flood-monitoring/id/floods?lat={lat}&long={lon}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json().get("items"):
            return "Zone 3 (High Risk)"
        return "Zone 1 or 2 (Low/Moderate Risk)"
    except:
        return "Unavailable"

def check_greenbelt(lat, lon):
    # Simulated check – replace with shapefile or API lookup in production
    return "No (Simulated)"

def get_topography(lat, lon):
    try:
        elev_url = f"https://api.opentopodata.org/v1/aster30m?locations={lat},{lon}"
        r = requests.get(elev_url, timeout=5)
        data = r.json()
        elevation = data['results'][0]['elevation']
        return f"{elevation:.1f} m elevation"
    except:
        return "Unavailable"

def get_utility_link(postcode):
    return f"https://lsbud.co.uk/"

# Processing
if postcode:
    lat, lon = geocode_postcode(postcode)
    if lat and lon:
        flood_result = get_flood_zone(lat, lon)
        greenbelt_result = check_greenbelt(lat, lon)
        elevation_result = get_topography(lat, lon)
        utility_result = get_utility_link(postcode)
    else:
        st.warning("Could not geocode postcode.")

# Display results
if lat and lon:
    st.markdown("### 📍 Site Details")
    st.write(f"**Postcode:** {postcode}")
    st.write(f"**Coordinates:** {lat:.5f}, {lon:.5f}")

    st.markdown("### 🌊 Flood Risk")
    st.write(f"**Flood Zone:** {flood_result}")

    st.markdown("### 🏞️ Planning Constraints")
    st.write(f"**Greenbelt:** {greenbelt_result}")
    st.write(f"**Topography:** {elevation_result}")

    st.markdown("### ⚡ Access & Utilities")
    st.write(f"**Utilities:** See [LSBUD]({utility_result})")
