import streamlit as st
from PIL import Image
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Batman BMI Tool", page_icon="🦇", layout="wide")

# ------------------ CUSTOM BATMAN THEME ------------------
st.markdown("""
    <style>
        body {background-color: #0D0D0D; color: #FFD700;}
        .stButton button {background-color: #FFD700; color: black; font-weight: bold;}
        .stDownloadButton button {background-color: #FFD700; color: black; font-weight: bold;}
        .stSlider, .stSelectbox, .stNumberInput {color: #FFD700;}
        h1, h2, h3, h4 {color: #FFD700 !important;}
    </style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("<h1 style='text-align:center;'>🦇 Batman BMI & Health Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>“It's not who I am underneath, but what I do that defines me.”</p>", unsafe_allow_html=True)
st.write("---")

# ------------------ BATMAN IMAGE ------------------
try:
    st.image("batman.png", use_column_width=True)  # Make sure you save 'batman.png' in repo
except:
    st.write("🦇 (Add batman.png to your folder for header image)")

# ------------------ INPUTS ------------------
unit_system = st.radio("Choose Unit System:", ["Metric (kg, cm)", "Imperial (lbs, inches)"])

if unit_system == "Metric (kg, cm)":
    weight = st.number_input("Weight (kg):", min_value=20.0, max_value=200.0, step=0.1)
    height = st.number_input("Height (cm):", min_value=100.0, max_value=250.0, step=0.1)
else:
    weight_lbs = st.number_input("Weight (lbs):", min_value=40.0, max_value=440.0, step=0.1)
    height_in = st.number_input("Height (inches):", min_value=40.0, max_value=100.0, step=0.1)
    weight = weight_lbs * 0.453592
    height = height_in * 2.54

age = st.slider("Age:", 5, 100, 25)
gender = st.selectbox("Gender:", ["Male", "Female", "Other"])
activity_level = st.select_slider("Activity Level:", ["Sedentary", "Light", "Moderate", "Very Active", "Extra Active"], value="Moderate")

# ------------------ BMI CALCULATION ------------------
height_m = height / 100
bmi = round(weight / (height_m ** 2), 1)

if bmi < 18.5:
    category, color, risk = "Underweight", "blue", "Higher risk of deficiency"
elif 18.5 <= bmi < 24.9:
    category, color, risk = "Normal", "green", "Low risk, maintain it"
elif 25 <= bmi < 29.9:
    category, color, risk = "Overweight", "orange", "Increased risk of disease"
else:
    category, color, risk = "Obese", "red", "High risk of heart/diabetes issues"

# ------------------ BMR & CALORIES ------------------
if gender == "Male":
    bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
elif gender == "Female":
    bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
else:
    bmr = (88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age) +
           447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)) / 2

activity_multipliers = {"Sedentary":
       
   
