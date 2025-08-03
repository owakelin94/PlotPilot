
import streamlit as st
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.image("plotpilot_logo.png", x=10, y=8, w=50)
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, "PlotPilot – Site Appraisal Summary", ln=True, align="C")
        self.ln(20)

    def chapter_body(self, text):
        self.set_font("DejaVu", "", 11)
        self.multi_cell(0, 10, text)

pdf = PDF()
pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
pdf.add_page()
pdf.chapter_body("Test summary – no errors expected 🚀")
pdf.output("example.pdf")
st.success("PDF generated successfully!")
