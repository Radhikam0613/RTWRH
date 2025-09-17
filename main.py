import streamlit as st
import pandas as pd
import math
import numpy as np
from io import BytesIO
from matplotlib import pyplot as plt

# Additional libs for PDF export 
from fpdf import FPDF

# Load rainfall data with caching for performance
@st.cache_data
def load_rainfall_data():
    df = pd.read_csv("rainfall-in-india-1901-2015.csv")
    # Clean and prepare unique regions list
    df["SUBDIVISION"] = df["SUBDIVISION"].str.strip()
    return df

df = load_rainfall_data()

# Dummy placeholder data for aquifer and water table info (would need real data API or DB)
aquifer_info = {
    "ANDAMAN & NICOBAR ISLANDS": "Principal Aquifer: Sandstone",
    "WEST BENGAL": "Principal Aquifer: Alluvial deposits",
    # Add more states/regions with real data here...
}

groundwater_depth = {
    "ANDAMAN & NICOBAR ISLANDS": 10,  # meters
    "WEST BENGAL": 7,
}

cost_estimate_per_m3 = 1000  # INR per cubic meter (example)
government_subsidy_pct = 30  # % subsidy example

# Regional language dictionary for demonstration (extendable)
languages = {
    "English": {"title": "Water Harvesting Calculator", "city": "Select City / State", "results": "Results"},
    "Hindi": {"title": "जल संचयन कैलकुलेटर", "city": "शहर / राज्य चुनें", "results": "परिणाम"},
}

# Language selection dropdown
region_lang = st.sidebar.selectbox("Select Language / भाषा चुनें", list(languages.keys()))
lang = languages.get(region_lang, languages["English"])


st.title(f"💧 {lang['title']} (Mahindra–TERI style)")

# --- User Inputs ---
st.header(lang["city"])
city = st.selectbox(lang["city"], df["SUBDIVISION"].unique())
city_data = df[df["SUBDIVISION"] == city]

# Current year average rainfall from dataset (last 10 years avg)
recent_years = city_data[city_data["YEAR"] > city_data["YEAR"].max() - 10]
avg_annual_rainfall = recent_years["ANNUAL"].mean()
avg_seasonal_rainfall = {
    "Jan-Feb": recent_years["Jan-Feb"].mean(),
    "Mar-May": recent_years["Mar-May"].mean(),
    "Jun-Sep": recent_years["Jun-Sep"].mean(),
    "Oct-Dec": recent_years["Oct-Dec"].mean(),
}

st.write(f"📊 Average Annual Rainfall (last 10 years): *{avg_annual_rainfall:.1f} mm*")
st.write("📅 Seasonal Rainfall (mm):")
st.write(avg_seasonal_rainfall)

# Catchment area
area = st.number_input("Catchment Area (m²)", min_value=10.0, value=100.0)

# Surface type -> runoff coefficient
surface_type = st.selectbox("Surface Type", ["Rooftop", "Paved", "Pervious"])
default_c = {
    "Rooftop": 0.85,
    "Paved": 0.7,
    "Pervious": 0.4,
}[surface_type]
c = st.slider("Runoff Coefficient (C)", 0.1, 1.0, float(default_c))

# First flush diversion
first_flush = st.number_input("First Flush Diversion (mm)", min_value=0.0, value=2.0)

# Efficiency factor
efficiency = st.slider("System Efficiency (%)", 50, 100, 90)

# --- Calculations ---
effective_rainfall = max(avg_annual_rainfall - first_flush, 0)
potential = area * c * effective_rainfall / 1000  # m³
harvestable = potential * (efficiency / 100)
harvestable_litres = harvestable * 1000

# Feasibility check (simple heuristic)
feasible = harvestable > 5  # sample threshold cubic meters

st.header(lang["results"])
st.write(f"🌧 Effective Rainfall: *{effective_rainfall:.2f} mm*")
st.write(f"📦 Harvestable Volume: *{harvestable:.2f} m³* (~{harvestable_litres:.0f} litres)")
st.write(f"✅ Feasibility: {'Yes' if feasible else 'No - Not suitable for RTRWH'}")

# Recharge structure design, suggested type and sizes
st.subheader("Recharge Structure Sizing & Recommendations")
recommended_structures = ["Recharge Pit", "Recharge Trench", "Recharge Shaft"]
structure_type = st.radio("Select Recharge Structure Type", recommended_structures)

if structure_type == "Recharge Pit":
    width = st.number_input("Recommended Width (m)", min_value=0.1, value=1.0)
    depth = st.number_input("Recommended Depth (m)", min_value=0.1, value=2.0)
    capacity = width * width * depth
elif structure_type == "Recharge Trench":
    length = st.number_input("Length (m)", min_value=0.1, value=5.0)
    width = st.number_input("Width (m)", min_value=0.1, value=1.0)
    depth = st.number_input("Depth (m)", min_value=0.1, value=1.0)
    capacity = length * width * depth
else:  # Shaft
    radius = st.number_input("Radius (m)", min_value=0.1, value=0.5)
    depth = st.number_input("Depth (m)", min_value=0.1, value=3.0)
    capacity = math.pi * radius**2 * depth

st.write(f"🛠 Structure Capacity: *{capacity:.2f} m³*")

# Principal aquifer and groundwater depth info
st.subheader("Groundwater Information")
st.write(f"Principal Aquifer in area: {aquifer_info.get(city, 'Data not available')}")
depth_gw = groundwater_depth.get(city, None)
if depth_gw:
    st.write(f"Depth to groundwater level: {depth_gw} meters")
else:
    st.write("Groundwater data not available")

# Cost estimate and subsidy info
st.subheader("Cost Estimation & Subsidy Information")
cost = harvestable * cost_estimate_per_m3
subsidy = (government_subsidy_pct / 100) * cost
net_cost = cost - subsidy

st.write(f"Approximate system cost: ₹{cost:,.0f}")
st.write(f"Estimated government subsidy (@{government_subsidy_pct}%): ₹{subsidy:,.0f}")
st.write(f"Net cost after subsidy: ₹{net_cost:,.0f}")

# Disclaimer
st.markdown("**Disclaimer:** The results provided are estimates for informational purposes only and should not be considered final engineering or design advice.")

# Maintenance notifications (sample)
st.subheader("Maintenance Notifications")
st.info("Check and clean gutters, screens, and first flush devices quarterly to ensure system efficiency.")

# Visualization of rainfall and structure capacity
st.subheader("Harvesting & Structure Capacity Visualization")
bar_data = {
    "Harvestable Volume (m³)": harvestable,
    "Recharge Structure Capacity (m³)": capacity,
}
st.bar_chart(bar_data)

# Export results to PDF (simple)
def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Water Harvesting Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"City/State: {city}", ln=True)
    pdf.cell(0, 10, f"Average Annual Rainfall: {avg_annual_rainfall:.2f} mm", ln=True)
    pdf.cell(0, 10, f"Harvestable Volume: {harvestable:.2f} m³", ln=True)
    pdf.cell(0, 10, f"Feasibility: {'Yes' if feasible else 'No'}", ln=True)
    pdf.cell(0, 10, f"Recharge Structure: {structure_type}", ln=True)
    pdf.cell(0, 10, f"Structure Capacity: {capacity:.2f} m³", ln=True)
    pdf.cell(0, 10, f"System Cost: ₹{cost:,.0f}", ln=True)
    pdf.cell(0, 10, f"Subsidy: ₹{subsidy:,.0f}", ln=True)
    pdf.cell(0, 10, f"Net Cost: ₹{net_cost:,.0f}", ln=True)
    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()

if st.button("Save / Export Report as PDF"):
    pdf_bytes = export_pdf()
    st.download_button("Download PDF Report", data=pdf_bytes, file_name="rainwater_harvesting_report.pdf")

# Animation placeholder (explanatory content)
st.subheader("What is Rooftop Rainwater Harvesting (RTRWH) & Artificial Recharge?")
st.video("https://www.youtube.com/watch?v=3F0MGHe0sbw")  # Example YouTube animated explainer

