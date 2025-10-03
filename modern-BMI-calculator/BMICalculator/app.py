import streamlit as st
from datetime import datetime
from io import BytesIO
from PIL import Image
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="Modern BMI & Health Dashboard",
    page_icon="🦇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ Session State ------------------
if 'history' not in st.session_state:
    st.session_state.history = []

# ------------------ Custom Styling ------------------
st.markdown("""
<style>
body {
    background-color: #1e1e1e;
    color: #f5f5f5;
}
h1, h2, h3, h4 {
    color: #FFD700;
}
.stSlider > div > div > div > div {
    background: #FFD700 !important;
}
.stButton>button {
    background-color: #FFD700;
    color: #1e1e1e;
}
</style>
""", unsafe_allow_html=True)

# ------------------ Helper Functions ------------------
def calculate_bmi(weight, height_m):
    bmi = round(weight / (height_m**2),1)
    if bmi < 18.5:
        category = "Underweight"
        risk = "Higher risk of nutritional deficiency and osteoporosis."
    elif 18.5 <= bmi < 24.9:
        category = "Normal"
        risk = "Low risk, maintain a healthy lifestyle."
    elif 25 <= bmi < 29.9:
        category = "Overweight"
        risk = "Increased risk of cardiovascular disease and diabetes."
    else:
        category = "Obese"
        risk = "High risk of heart disease, diabetes, joint problems, sleep apnea."
    return bmi, category, risk

def calculate_bmr(weight, height_cm, age, gender):
    if gender == "Male":
        bmr = 88.362 + (13.397*weight) + (4.799*height_cm) - (5.677*age)
    elif gender == "Female":
        bmr = 447.593 + (9.247*weight) + (3.098*height_cm) - (4.330*age)
    else:
        bmr_m = 88.362 + (13.397*weight) + (4.799*height_cm) - (5.677*age)
        bmr_f = 447.593 + (9.247*weight) + (3.098*height_cm) - (4.330*age)
        bmr = (bmr_m + bmr_f)/2
    return round(bmr,1)

def generate_pdf(weight, height_cm, age, gender, bmi, category, risk, ideal_min, ideal_max, bmr, activity_level, daily_calories, body_fat, water_intake, protein):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#FFD700'), alignment=1, spaceAfter=20)
    story.append(Paragraph("BMI Calculator & Health Dashboard", title_style))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1,0.3*inch))

    # BMI Table
    story.append(Paragraph("<b>Your BMI Results</b>", styles['Heading2']))
    bmi_data = [
        ['Metric','Value'],
        ['Weight', f'{weight} kg'],
        ['Height', f'{height_cm} cm'],
        ['Age', f'{age} years'],
        ['Gender', gender],
        ['BMI', f'{bmi} ({category})'],
        ['Health Risk', risk]
    ]
    table = Table(bmi_data, colWidths=[3*inch,3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#FFD700')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige)
    ]))
    story.append(table)
    story.append(Spacer(1,0.3*inch))

    # Recommendations
    story.append(Paragraph("<b>Personalized Recommendations</b>", styles['Heading2']))
    rec_data = [
        ['Recommendation','Value'],
        ['Ideal Weight Range', f'{ideal_min} - {ideal_max} kg'],
        ['BMR', f'{bmr} kcal/day'],
        ['Activity Level', activity_level],
        ['Daily Calories', f'{daily_calories} kcal/day'],
        ['Estimated Body Fat', f'{body_fat}%'],
        ['Daily Water Intake', f'{water_intake} ml'],
        ['Daily Protein Need', f'{protein} g']
    ]
    table2 = Table(rec_data, colWidths=[3*inch,3*inch])
    table2.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#FFD700')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige)
    ]))
    story.append(table2)
    story.append(Spacer(1,0.3*inch))

    # Health Tips
    story.append(Paragraph("<b>Health Tips</b>", styles['Heading2']))
    tips = [
        "Maintain a balanced diet with variety of nutrients",
        "Stay active with daily exercise",
        "Drink adequate water throughout the day",
        "Monitor your BMI and BMR regularly",
        "Get 7-9 hours of sleep per night",
        "Consult healthcare professionals if necessary"
    ]
    for t in tips:
        story.append(Paragraph(f"• {t}", styles['Normal']))

    story.append(Spacer(1,0.3*inch))
    story.append(Paragraph("Created by Faizan Shah Khan | Modern BMI Tool", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ------------------ App Title ------------------
st.markdown("<h1 style='text-align:center'>🦇 Modern BMI & Health Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Interactive BMI & BMR tool with health recommendations</p>", unsafe_allow_html=True)
st.write("---")

# ------------------ Inputs ------------------
col1, col2 = st.columns(2)
with col1:
    weight = st.number_input("Weight (kg):", 20, 200, 70)
with col2:
    height_cm = st.number_input("Height (cm):", 100, 220, 170)

age = st.number_input("Age:", 5, 100, 25)
gender = st.selectbox("Gender:", ["Male","Female","Other"])

activity_level = st.select_slider("Activity Level:", options=["Sedentary","Light","Moderate","Very Active","Extra Active"], value="Moderate")

# ------------------ BMI Calculation ------------------
height_m = height_cm/100
bmi, category, risk = calculate_bmi(weight, height_m)
ideal_min = round(18.5*(height_m**2),1)
ideal_max = round(24.9*(height_m**2),1)
bmr = calculate_bmr(weight, height_cm, age, gender)

activity_multipliers = {
    "Sedentary":1.2,
    "Light":1.375,
    "Moderate":1.55,
    "Very Active":1.725,
    "Extra Active":1.9
}
daily_calories = round(bmr * activity_multipliers[activity_level])

body_fat = max(0, min(60, round((1.20*bmi)+(0.23*age) - (16.2 if gender=="Male" else 5.4),1)))
water_intake = round(weight*35)
protein = round(weight*0.8)

# Save to session history
st.session_state.history.append({
    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "weight": weight,
    "height": height_cm,
    "bmi": bmi,
    "bmr": bmr
})

# ------------------ Display Results ------------------
st.subheader("Your BMI Results")
st.metric("BMI Value", f"{bmi} ({category})")
st.info(f"Health Risk: {risk}")
st.write(f"Ideal Weight: {ideal_min} – {ideal_max} kg")
st.write(f"Activity Level: {activity_level}")
st.write(f"Recommended Daily Calories: {daily_calories} kcal/day")
st.write(f"Estimated Body Fat: {body_fat}%")
st.write(f"Daily Water Intake: {water_intake} ml")
st.write(f"Daily Protein Requirement: {protein} g")
st.write(f"BMR: {bmr} kcal/day")

# ------------------ BMI Gauge ------------------
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=bmi,
    title={'text':"BMI Gauge"},
    gauge={'axis':{'range':[10,50]},
           'bar':{'color':'#FFD700'},
           'steps':[
               {'range':[10,18.5],'color':'lightblue'},
               {'range':[18.5,24.9],'color':'lightgreen'},
               {'range':[25,29.9],'color':'orange'},
               {'range':[30,50],'color':'red'}
           ],
           'threshold':{'line':{'color':'red','width':4},'thickness':0.75,'value':25}}
))
fig.update_layout(height=300)
st.plotly_chart(fig,use_container_width=True)

# ------------------ BMR Chart ------------------
st.subheader("BMR vs Activity Level")
bmr_fig = go.Figure()
for level,mult in activity_multipliers.items():
    bmr_fig.add_trace(go.Bar(
        x=[level],
        y=[round(bmr*mult)],
        name=level,
        text=f"{round(bmr*mult)} kcal",
        textposition="auto"
    ))
bmr_fig.update_layout(yaxis_title="Calories", xaxis_title="Activity Level", height=350)
st.plotly_chart(bmr_fig,use_container_width=True)

# ------------------ Session History ------------------
st.subheader("Session BMI & BMR History")
history_df = st.session_state.history[::-1]  # Reverse chronological
for record in history_df[:10]:
    st.write(f"{record['date']}: BMI {record['bmi']}, BMR {record['bmr']} kcal, Weight {record['weight']} kg, Height {record['height']} cm")

# ------------------ PDF Download ------------------
pdf_buffer = generate_pdf(weight, height_cm, age, gender, bmi, category, risk, ideal_min, ideal_max, bmr, activity_level, daily_calories, body_fat, water_intake, protein)
st.download_button("📄 Download Full Report (PDF)", data=pdf_buffer, file_name=f"BMI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf")

# ------------------ Share Result ------------------
st.subheader("Share Your Results")
st.code(f"BMI: {bmi} ({category}) | BMR: {bmr} kcal | Ideal Weight: {ideal_min}-{ideal_max} kg | Activity Level: {activity_level} | Protein: {protein} g | Water: {water_intake} ml")

st.markdown("<p style='text-align:center;'>🦇 Built by Faizan Shah Khan | Modern BMI Tool</p>", unsafe_allow_html=True)
