
import streamlit as st
from geopy.geocoders import Nominatim
import requests

st.set_page_config(page_title="PlotPilot", layout="centered")
st.title("📍 PlotPilot – AI Land Appraisal Tool")
st.subheader("Automated Site Viability Screening")

# ---- Functions ----
def get_coordinates(address):
    geolocator = Nominatim(user_agent="plotpilot")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None

def check_flood_zone(lat, lon):
    url_template = "https://environment.data.gov.uk/arcgis/rest/services/FloodMapForPlanning/MapServer/{zone}/query"
    for zone, label in [(3, "3 (High Risk)"), (2, "2 (Moderate Risk)")]:
        params = {
            "geometry": f"{lon},{lat}",
            "geometryType": "esriGeometryPoint",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "returnGeometry": "false",
            "outFields": "*",
            "f": "json"
        }
        url = url_template.format(zone=zone)
        response = requests.get(url, params=params)
        if response.ok and response.json().get("features"):
            return label
    return "1 (Low Risk)"

# ---- App UI ----
st.markdown("### 📝 Enter Site Address")
address = st.text_input("Site Address", placeholder="e.g. Land north of Oakfield Lane, Bicester")
greenbelt = st.selectbox("Greenbelt", ["No", "Yes", "Adjacent", "Unknown"])
access_quality = st.selectbox("Access Type", ["Direct from road", "Shared private drive", "Unclear", "No access"])
topo_slope = st.selectbox("Topography", ["Flat", "Gentle", "Steep", "Unknown"])
utilities = st.selectbox("Nearby Utilities (within 25m)", ["Yes", "No", "Unknown"])
submit = st.button("🔍 Analyse Site")

if submit:
    st.markdown("### 📋 Appraisal Result")
    lat, lon = get_coordinates(address)
    if not lat:
        st.error("❌ Could not geocode address.")
    else:
        with st.spinner("Detecting flood zone..."):
            flood_zone = check_flood_zone(lat, lon)
        score = 10
        if "3" in flood_zone: score -= 4
        elif "2" in flood_zone: score -= 2
        if greenbelt in ["Yes", "Adjacent"]: score -= 2
        if access_quality in ["Unclear", "No access"]: score -= 2
        if topo_slope == "Steep": score -= 1
        if utilities == "No": score -= 1
        if score >= 7:
            status = "🟢 GREEN – Low risk"
        elif score >= 4:
            status = "🟠 AMBER – Moderate risk"
        else:
            status = "🔴 RED – High risk"
        st.markdown(f"**Viability Score:** `{score} / 10` — {status}")
        st.markdown("### Summary")
        st.code(f"""Address: {address}
Flood Zone: {flood_zone}
Greenbelt: {greenbelt}
Access: {access_quality}
Topography: {topo_slope}
Utilities Nearby: {utilities}

AI Insight:
This site presents a {status.lower()} opportunity. Engineering risks may include {"flooding, " if "3" in flood_zone else ""}{"access constraints, " if access_quality in ["Unclear", "No access"] else ""}{"limited utility connections" if utilities == "No" else "standard review"}.
""")
