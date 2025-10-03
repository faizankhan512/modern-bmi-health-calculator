import streamlit as st
from PIL import Image
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import math

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="🦇 Modern BMI & BMR Dashboard",
    page_icon="🦇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------ Custom CSS / Batman Theme ------------------
st.markdown("""
<style>
body {
    background-color: #1c1c1c;
    color: #f0f0f0;
}
h1, h2, h3, h4 {
    color: #FFD700;
}
.stButton>button {
    background-color: #FFD700;
    color: #000000;
    font-weight: bold;
}
.stSlider>div>div>div>div>div {
    background-color: #444444;
}
.stSlider>div>div>div>div>div>div {
    background-color: #FFD700;
}
</style>
""", unsafe_allow_html=True)

# ------------------ Functions ------------------
def generate_pdf(weight, height, age, gender, bmi, category, risk, ideal_min, ideal_max, bmr, activity_level, daily_calories, body_fat, water_intake, protein):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#FFD700'), alignment=1, spaceAfter=20)
    story.append(Paragraph("🦇 Modern BMI & BMR Dashboard", title_style))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    # BMI Data Table
    bmi_data = [
        ['Metric', 'Value'],
        ['Weight', f'{weight} kg'],
        ['Height', f'{height} cm'],
        ['Age', f'{age} years'],
        ['Gender', gender],
        ['BMI', f'{bmi} ({category})'],
        ['Health Risk', risk],
    ]
    bmi_table = Table(bmi_data, colWidths=[3*inch, 3*inch])
    bmi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFD700')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0),12),
        ('BOTTOMPADDING',(0,0),(-1,0),8),
        ('BACKGROUND',(0,1),(-1,-1),colors.HexColor('#2b2b2b')),
        ('TEXTCOLOR',(0,1),(-1,-1),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.white)
    ]))
    story.append(bmi_table)
    story.append(Spacer(1, 0.2*inch))

    # Recommendations Table
    rec_data = [
        ['Recommendation', 'Value'],
        ['Ideal Weight Range', f'{ideal_min}-{ideal_max} kg'],
        ['Activity Level', activity_level],
        ['BMR', f'{round(bmr)} kcal/day'],
        ['Daily Calories', f'{daily_calories} kcal/day'],
        ['Body Fat %', f'{body_fat}%'],
        ['Water Intake', f'{water_intake} ml/day'],
        ['Protein', f'{protein} g/day']
    ]
    rec_table = Table(rec_data, colWidths=[3*inch,3*inch])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFD700')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0),12),
        ('BOTTOMPADDING',(0,0),(-1,0),8),
        ('BACKGROUND',(0,1),(-1,-1),colors.HexColor('#2b2b2b')),
        ('TEXTCOLOR',(0,1),(-1,-1),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.white)
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 0.2*inch))

    # Health Tips
    story.append(Paragraph("<b>Health Tips:</b>", styles['Heading2']))
    tips = [
        "Maintain a balanced diet with proper calories",
        "Stay hydrated with at least 30-40 ml/kg water",
        "Do 150 min/week of moderate exercise",
        "Monitor BMI and body fat regularly",
        "Get 7-9 hours of sleep per night",
        "Manage stress through mindfulness"
    ]
    for tip in tips:
        story.append(Paragraph(f"• {tip}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("🦇 Built by Faizan Shah Khan | Batman Theme", styles['Normal']))
    doc.build(story)
    buffer.seek(0)
    return buffer

# ------------------ Input Section ------------------
st.markdown("<h1 style='text-align:center'>🦇 Modern BMI & BMR Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Calculate BMI, BMR and get health tips!</p>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns(2)
with col1:
    weight = st.slider("Weight (kg):", 20, 200, 70)
with col2:
    height_cm = st.slider("Height (cm):", 100, 220, 170)

age = st.slider("Age (years):", 5, 100, 25)
gender = st.selectbox("Gender:", ["Male","Female","Other"])

activity_level = st.select_slider("Activity Level:",
    options=["Sedentary","Light","Moderate","Very Active","Extra Active"], value="Moderate")

# ------------------ Calculations ------------------
height_m = height_cm / 100
bmi = round(weight / (height_m**2),1)
ideal_min = round(18.5*(height_m**2),1)
ideal_max = round(24.9*(height_m**2),1)

# BMI category
if bmi < 18.5:
    category = "Underweight"
    risk = "Higher risk of nutritional deficiency, osteoporosis"
elif bmi < 25:
    category = "Normal"
    risk = "Low risk, maintain healthy lifestyle"
elif bmi < 30:
    category = "Overweight"
    risk = "Increased risk of heart disease, diabetes"
else:
    category = "Obese"
    risk = "High risk of heart disease, diabetes, other health issues"

# BMR Calculation (Harris-Benedict)
if gender=="Male":
    bmr = 88.362 + (13.397*weight) + (4.799*height_cm) - (5.677*age)
elif gender=="Female":
    bmr = 447.593 + (9.247*weight) + (3.098*height_cm) - (4.330*age)
else:
    bmr_m = 88.362 + (13.397*weight) + (4.799*height_cm) - (5.677*age)
    bmr_f = 447.593 + (9.247*weight) + (3.098*height_cm) - (4.330*age)
    bmr = (bmr_m + bmr_f)/2

# Activity multipliers
activity_multipliers = {"Sedentary":1.2,"Light":1.375,"Moderate":1.55,"Very Active":1.725,"Extra Active":1.9}
daily_calories = round(bmr*activity_multipliers[activity_level])

# Body fat, water, protein
if gender=="Male":
    body_fat = round((1.20*bmi)+(0.23*age)-16.2,1)
else:
    body_fat = round((1.20*bmi)+(0.23*age)-5.4,1)
body_fat = max(0,min(60,body_fat))
water_intake = round(weight*35)
protein = round(weight*0.8)

# ------------------ Display ------------------
st.markdown(f"*BMI:* {bmi} ({category}) | *Health Risk:* {risk}")
st.markdown(f"*Ideal Weight Range:* {ideal_min} - {ideal_max} kg")
st.markdown(f"*Daily Calories:* {daily_calories} kcal | *BMR:* {round(bmr)} kcal/day")
st.markdown(f"*Body Fat:* {body_fat}% | *Water Intake:* {water_intake} ml | *Protein:* {protein} g")

# ------------------ BMR Interactive Chart ------------------
st.markdown("### 🦇 BMR & Calorie Breakdown")
fig_bmr = go.Figure()
fig_bmr.add_trace(go.Bar(name="BMR", x=["BMR"], y=[round(bmr)], marker_color="#FFD700"))
fig_bmr.add_trace(go.Bar(name="Daily Calories", x=["Calories Needed"], y=[daily_calories], marker_color="#FF8C00"))
fig_bmr.update_layout(barmode='group', template='plotly_dark', yaxis_title="kcal")
st.plotly_chart(fig_bmr, use_container_width=True)

# Health Suggestions based on BMI
st.markdown("### 🦇 Health Suggestions")
suggestions = [
    f"Maintain weight within {ideal_min}-{ideal_max} kg",
    f"Drink at least {water_intake} ml water daily",
    f"Consume {protein} g protein daily",
    "Do 150 min/week moderate exercise",
    "Sleep 7-9 hours nightly",
    "Regular health check-ups recommended"
]
for s in suggestions:
    st.write("• "+s)

# ------------------ PDF Download ------------------
if st.button("📄 Download PDF Report"):
    pdf_buffer = generate_pdf(weight,height_cm,age,gender,bmi,category,risk,ideal_min,ideal_max,bmr,activity_level,daily_calories,body_fat,water_intake,protein)
    st.download_button("Download Report", data=pdf_buffer, file_name=f"BMI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf")

# ------------------ Share Result ------------------
st.markdown("### 🦇 Share Your Result")
st.text_area("Copy your results:", value=f"BMI: {bmi} ({category}) | BMR: {round(bmr)} kcal | Calories: {daily_calories} kcal | Water: {water_intake} ml | Protein: {protein} g", height=100)
st.markdown("<p style='text-align:center;'>🦇 Built by Faizan Shah Khan | Batman Theme</p>", unsafe_allow_html=True)
