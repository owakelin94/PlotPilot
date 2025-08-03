
import streamlit as st
from geopy.geocoders import Nominatim
import requests

st.set_page_config(page_title="PlotPilot", layout="centered")
st.title("📍 PlotPilot – AI Land Appraisal Tool")
st.subheader("Flood Zone Auto-Detection Prototype")

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

st.markdown("### 🔍 Enter Site Address")
address = st.text_input("Site Address", placeholder="e.g. Land north of Oakfield Lane, Bicester")

if address:
    with st.spinner("Looking up flood zone..."):
        lat, lon = get_coordinates(address)
        if lat and lon:
            flood_zone_result = check_flood_zone(lat, lon)
            st.success(f"✅ Flood Zone for this site: **Zone {flood_zone_result}**")
        else:
            st.error("❌ Unable to geocode that address.")
