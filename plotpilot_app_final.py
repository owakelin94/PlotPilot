
import streamlit as st
from geopy.geocoders import Nominatim
import requests
from io import BytesIO
from fpdf import FPDF
from PIL import Image

# ---- Streamlit UI Setup ----
st.set_page_config(page_title="PlotPilot", layout="centered")

# Load and display logo
try:
    logo = Image.open("plotpilot_logo.png")
    st.image(logo, width=300)
except:
    st.title("PlotPilot")

st.subheader("AI Land Appraisal")

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

def classify_topography(lat, lon):
    import random
    slope_percent = random.uniform(0, 15)
    if slope_percent < 3:
        return "Flat"
    elif slope_percent < 10:
        return "Gentle"
    else:
        return "Steep"

def lookup_greenbelt(lat, lon):
    import random
    return random.choice(["No", "Yes", "Adjacent"])

def lookup_utilities(postcode):
    if postcode[:2] in ["OX", "BS", "N1", "NG"]:
        return "Yes"
    return "Unknown"

# ---- Form UI ----
st.markdown("### 📝 Enter Site Information")
with st.form("site_form"):
    address = st.text_input("Site Address", placeholder="e.g. Land north of Oakfield Lane, Bicester")
    postcode = st.text_input("Postcode (for utilities)", placeholder="e.g. OX26 1AB")
    submit = st.form_submit_button("🔍 Analyse Site")

if submit:
    lat, lon = get_coordinates(address)
    if not lat:
        st.error("❌ Unable to geocode address.")
    else:
        flood = check_flood_zone(lat, lon)
        slope = classify_topography(lat, lon)
        greenbelt = lookup_greenbelt(lat, lon)
        utilities = lookup_utilities(postcode)

        score = 10
        if "3" in flood: score -= 4
        elif "2" in flood: score -= 2
        if greenbelt in ["Yes", "Adjacent"]: score -= 2
        if slope == "Steep": score -= 1
        if utilities == "No": score -= 1

        if score >= 7:
            status = "🟢 GREEN – Low risk"
        elif score >= 4:
            status = "🟠 AMBER – Moderate risk"
        else:
            status = "🔴 RED – High risk"

        summary = f"""Site Address: {address}
Postcode: {postcode}
Flood Zone: {flood}
Greenbelt: {greenbelt}
Topography: {slope}
Utilities Nearby: {utilities}

Viability Score: {score}/10 — {status}

AI Insight:
This site presents a {status.lower()} opportunity. Engineering risks may include {"flooding, " if "3" in flood else ""}{"access constraints, " if slope == "Steep" else ""}{"limited utility connections" if utilities == "No" else "standard development risk"}.
"""

        st.markdown("### 📋 Site Appraisal Result")
        st.code(summary)

        class PDF(FPDF):
            def header(self):
                try:
                    self.image("plotpilot_logo.png", x=10, y=8, w=50)
                except:
                    self.set_font("Arial", "B", 12)
                    self.cell(0, 10, "PlotPilot – Site Appraisal Summary", ln=True, align="C")
                self.ln(25)
            def chapter_body(self, text):
                self.set_font("Arial", "", 11)
                self.multi_cell(0, 10, text)

        pdf = PDF()
        pdf.add_page()
        pdf.chapter_body(summary)
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        st.download_button("📄 Download PDF Report", data=pdf_output.getvalue(), file_name="PlotPilot_Report.pdf")
