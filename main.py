import streamlit as st
import pandas as pd
import math

# Load dataset (use the CSV we generated earlier)
@st.cache_data
def load_data():
    return pd.read_csv("water_dataset_india_sample.csv")

df = load_data()

st.title("💧 Water Harvesting Calculator (Mahindra–TERI style)")

# --- User Inputs ---
st.header("Input Parameters")

# City selection
city = st.selectbox("Select City / State", df["City/State"].unique())
rainfall = df.loc[df["City/State"] == city, "Annual Rainfall (mm)"].values[0]

st.write(f"📊 Average annual rainfall for {city}: *{rainfall} mm*")

# Catchment area
area = st.number_input("Catchment Area (m²)", min_value=10.0, value=100.0)

# Surface type -> runoff coefficient
surface_type = st.selectbox("Surface Type", ["Rooftop", "Paved", "Pervious"])
default_c = {
    "Rooftop": 0.85,
    "Paved": 0.7,
    "Pervious": 0.4
}[surface_type]

c = st.slider("Runoff Coefficient (C)", 0.1, 1.0, float(default_c))

# First flush diversion
first_flush = st.number_input("First Flush Diversion (mm)", min_value=0.0, value=2.0)

# Efficiency factor
efficiency = st.slider("System Efficiency (%)", 50, 100, 90)

# --- Calculations ---
effective_rainfall = max(rainfall - first_flush, 0)
potential = area * c * effective_rainfall / 1000  # m³
harvestable = potential * (efficiency / 100)
harvestable_litres = harvestable * 1000

# --- Results ---
st.header("Results")
st.write(f"🌧 Effective Rainfall: *{effective_rainfall:.2f} mm*")
st.write(f"📦 Harvestable Volume: *{harvestable:.2f} m³* (~{harvestable_litres:.0f} litres)")

# Recharge structure design
st.subheader("Recharge Structure Sizing")

shape = st.radio("Select Structure Shape", ["Cuboidal", "Cylindrical"])

if shape == "Cuboidal":
    L = st.number_input("Length (m)", min_value=0.1, value=2.0)
    B = st.number_input("Breadth (m)", min_value=0.1, value=2.0)
    H = st.number_input("Height (m)", min_value=0.1, value=2.0)
    capacity = L * B * H
    surface_area = (L * B) + 2 * (L * H) + 2 * (B * H)
elif shape == "Cylindrical":
    r = st.number_input("Radius (m)", min_value=0.1, value=1.0)
    h = st.number_input("Height (m)", min_value=0.1, value=2.0)
    capacity = math.pi * r**2 * h
    surface_area = (math.pi * r**2) + (2 * math.pi * r * h)

st.write(f"🛠 Structure Capacity: *{capacity:.2f} m³*")
st.write(f"📐 Recharge Surface Area: *{surface_area:.2f} m²*")

# --- Optional Visualization ---
st.subheader("Visualization")
st.bar_chart({
    "Harvestable Rainwater (m³)": [harvestable],
    "Structure Capacity (m³)": [capacity]
})