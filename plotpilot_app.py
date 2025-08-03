
import streamlit as st
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="PlotPilot", layout="centered")
st.title("📍 PlotPilot – AI Land Appraisal Tool")
st.subheader("Instant site insight for small-scale residential development")

st.markdown("### 📝 Site Information")
with st.form("site_form"):
    site_address = st.text_input("Site Address", placeholder="e.g. Land north of Oakfield Lane, Bicester")
    flood_zone = st.selectbox("Flood Zone", ["1 (Low Risk)", "2 (Moderate)", "3 (High Risk)", "Unknown"])
    greenbelt = st.selectbox("Greenbelt", ["No", "Yes", "Adjacent", "Unknown"])
    access_quality = st.selectbox("Access Type", ["Direct from road", "Shared private drive", "Unclear", "No access"])
    topo_slope = st.selectbox("Topography", ["Flat", "Gentle", "Steep", "Unknown"])
    utilities = st.selectbox("Nearby Utilities (within 25m)", ["Yes", "No", "Unknown"])
    submit_button = st.form_submit_button("🔍 Analyse Site")

if submit_button:
    st.markdown("### 📋 Site Appraisal Summary")
    score = 10
    if flood_zone == "3 (High Risk)": score -= 4
    elif flood_zone == "2 (Moderate)": score -= 2
    if greenbelt in ["Yes", "Adjacent"]: score -= 2
    if access_quality in ["Unclear", "No access"]: score -= 2
    if topo_slope == "Steep": score -= 1
    if utilities == "No": score -= 1
    status = "🟢 GREEN – Low risk"
    if score <= 6: status = "🟠 AMBER – Moderate risk"
    if score <= 3: status = "🔴 RED – High risk"

    st.markdown(f"**Viability Score:** `{score} / 10` — {status}")
    summary = f'''
- **Address:** {site_address}
- **Flood Zone:** {flood_zone}
- **Greenbelt:** {greenbelt}
- **Access:** {access_quality}
- **Topography:** {topo_slope}
- **Utilities Nearby:** {utilities}

**AI Insight:**
This site presents a {status.lower()} opportunity for development. Engineering risks may include {("flooding, " if "3" in flood_zone else "")}{("access constraints, " if access_quality in ["Unclear", "No access"] else "")}{("limited utility connections" if utilities == "No" else "standard infrastructure review")}.
'''
    st.code(summary)

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "PlotPilot – Site Appraisal Summary", ln=True, align="C")
        def chapter_body(self, text):
            self.set_font("Arial", "", 11)
            self.multi_cell(0, 10, text)

    pdf = PDF()
    pdf.add_page()
    pdf.chapter_body(summary)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    st.download_button("📄 Download PDF Report", data=pdf_output.getvalue(), file_name="PlotPilot_Report.pdf")
