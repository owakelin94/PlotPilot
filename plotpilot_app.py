
import streamlit as st
from fpdf import FPDF
import requests
from geopy.geocoders import Nominatim

st.set_page_config(page_title="PlotPilot – AI Land Appraisal")
st.title("PlotPilot")
st.subheader("AI Land Appraisal")

# --- Functions ---
def geocode_postcode(postcode):
    geolocator = Nominatim(user_agent="plotpilot")
    location = geolocator.geocode(postcode)
    if location:
        return location.latitude, location.longitude
    return None, None

def get_flood_zone(lat, lon):
    url = f"https://environment.data.gov.uk/flood-monitoring/id/floods?lat={lat}&long={lon}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("items"):
                return "Zone 3 (High Risk)"
            else:
                return "Zone 1 or 2 (Low/Moderate Risk)"
        return "Flood zone data unavailable"
    except:
        return "Error fetching flood data"

class PDF(FPDF):
    def header(self):
        self.image("assets/logo.png", x=10, y=8, w=40)
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 10, "PlotPilot – Site Appraisal Summary", ln=True, align="C")
        self.ln(20)

    def chapter_body(self, text):
        self.set_font("DejaVu", "", 12)
        self.multi_cell(0, 10, text)

# --- UI ---
postcode = st.text_input("Enter postcode for appraisal:")
flood_zone_result = "Not checked"

if postcode:
    lat, lon = geocode_postcode(postcode)
    if lat and lon:
        flood_zone_result = get_flood_zone(lat, lon)
        st.success(f"Flood Zone: {flood_zone_result}")
    else:
        st.error("Could not geocode the postcode.")

if st.button("Generate PDF"):
    pdf = PDF()
    pdf.add_font("DejaVu", "", "assets/fonts/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "assets/fonts/DejaVuSans-Bold.ttf", uni=True)
    pdf.add_page()
    content = f"Site appraisal for postcode: {postcode or 'N/A'}\n\nFlood Zone: {flood_zone_result}"
    pdf.chapter_body(content)

    pdf_path = "PlotPilot_Report.pdf"
    pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button("Download Report", f, file_name=pdf_path)
