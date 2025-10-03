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
    .stButton button, .stDownloadButton button {background-color: #FFD700; color: black; font-weight: bold;}
    .stSlider, .stSelectbox, .stNumberInput {color: #FFD700;}
    h1, h2, h3, h4 {color: #FFD700 !important;}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("<h1 style='text-align:center;'>🦇 Batman BMI & Health Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>“It's not who I am underneath, but what I do that defines me.”</p>", unsafe_allow_html=True)
st.write("---")

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
    bmr_male = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    bmr_female = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    bmr = (bmr_male + bmr_female) / 2

activity_multipliers = {
    "Sedentary": 1.2,
    "Light": 1.375,
    "Moderate": 1.55,
    "Very Active": 1.725,
    "Extra Active": 1.9
}

daily_calories = round(bmr * activity_multipliers[activity_level])

# ------------------ DISPLAY RESULTS ------------------
st.subheader("Your BMI Results 🦇")
st.metric("BMI", f"{bmi} ({category})")
st.info(f"Risk: {risk}")
st.write(f"Ideal Weight: {round(18.5*(height_m*2),1)} – {round(24.9(height_m**2),1)} kg")
st.write(f"BMR: {round(bmr)} kcal/day")
st.write(f"Calories Needed: {daily_calories} kcal/day")

# ------------------ BMI GAUGE ------------------
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=bmi,
    title={'text': "BMI Gauge"},
    gauge={
        'axis': {'range': [10, 40]},
        'bar': {'color': color},
        'steps': [
            {'range': [10, 18.5], 'color': "lightblue"},
            {'range': [18.5, 24.9], 'color': "lightgreen"},
            {'range': [25, 29.9], 'color': "#FFE4B5"},
            {'range': [30, 40], 'color': "lightcoral"}
        ]
    }
))
st.plotly_chart(fig, use_container_width=True)

# ------------------ BMI COMPARISON ------------------
st.subheader("BMI Range Comparison")
fig_comparison = go.Figure()
categories_ranges = [
    ("Underweight", 10, 18.5, "lightblue"),
    ("Normal", 18.5, 24.9, "lightgreen"),
    ("Overweight", 25, 29.9, "#FFE4B5"),
    ("Obese", 30, 40, "lightcoral")
]
for cat, start, end, color_bar in categories_ranges:
    fig_comparison.add_trace(go.Bar(
        x=[end - start],
        y=[cat],
        orientation='h',
        base=start,
        marker=dict(color=color_bar),
        name=cat,
        text=f"{start}-{end}",
        textposition="inside",
        hovertemplate=f"{cat}: {start}-{end}<extra></extra>"
    ))

# User marker
fig_comparison.add_trace(go.Scatter(
    x=[bmi],
    y=[category],
    mode='markers+text',
    marker=dict(color='red', size=15, symbol='diamond', line=dict(color='darkred', width=2)),
    text=f"You: {bmi}",
    textposition="top center"
))
fig_comparison.update_layout(height=300, xaxis=dict(range=[10,40]), barmode='overlay')
st.plotly_chart(fig_comparison, use_container_width=True)

# ------------------ SESSION HISTORY ------------------
if "history" not in st.session_state:
    st.session_state["history"] = []

if st.button("💾 Save This Result"):
    st.session_state["history"].append({
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Weight": round(weight,1),
        "Height": round(height,1),
        "BMI": bmi
    })
    st.success("Saved in session (clears on refresh)")

if st.session_state["history"]:
    st.subheader("Session History 📈")
    st.dataframe(pd.DataFrame(st.session_state["history"]))

# ------------------ PDF DOWNLOAD ------------------
def generate_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, textColor=colors.HexColor('#FFD700'), alignment=1)
    story.append(Paragraph("🦇 Batman BMI Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))

    bmi_data = [
        ['Metric', 'Value'],
        ['BMI', f"{bmi} ({category})"],
        ['Weight', f"{round(weight,1)} kg"],
        ['Height', f"{round(height,1)} cm"],
        ['Age', age],
        ['Gender', gender],
        ['BMR', f"{round(bmr)} kcal/day"],
        ['Calories Needed', f"{daily_calories} kcal/day"],
        ['Risk', risk]
    ]
    table = Table(bmi_data, colWidths=[3*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFD700')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))

    doc.build(story)
    buffer.seek(0)
    return buffer

st.download_button("📄 Download PDF Report", generate_pdf(), file_name="Batman_BMI_Report.pdf", mime="application/pdf")

# ------------------ SHARE RESULT ------------------
share_text = f"My BMI is {bmi} ({category}), BMR: {round(bmr)} kcal/day, Calories needed: {daily_calories} kcal/day."
st.text_area("Copy & Share Your Result:", share_text)

# ------------------ FOOTER ------------------
st.write("---")
st.markdown("<p style='text-align:center;'>🦇 Built by Faizan Shah Khan | Batman BMI Tool</p>", unsafe_allow_html=True)
