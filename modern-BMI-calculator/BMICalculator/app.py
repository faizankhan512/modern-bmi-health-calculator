import streamlit as st
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import plotly.graph_objects as go

st.set_page_config(
    page_title="BMI Calculator Dashboard",
    page_icon="🏋",
    layout="wide"
)

# ------------------ Dashboard Title with Metallic Effect ------------------
st.markdown(
    """
    <h1 style='
        text-align: center;
        font-size: 48px;
        font-weight: 900;
        background: linear-gradient(90deg, #FFD700, #FFA500, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        font-family: "Arial Black", sans-serif;
        margin-bottom: 10px;
    '>
        🦇 BMI Calculator & Health Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)
# ------------------ Motivational Fitness Quote ------------------
st.markdown(
    """
    <div style='
        text-align: center; 
        font-size: 18px; 
        font-weight: bold; 
        color: #FFD700; 
        background-color: rgba(0,0,0,0.5); 
        padding: 8px; 
        border-radius: 8px;
        margin-bottom: 20px;
    '>
        "Fitness is not about being better than someone else; it’s about being better than you used to be." 🌟
    </div>
    """, unsafe_allow_html=True
)

# ------------------ Custom CSS / Batman Dark Theme ------------------
st.markdown("""
<style>
body {background-color: #1c1c1c; color: #f0f0f0;}
h1, h2, h3, h4 {color: #FFD700;}
.stButton>button {background-color: #FFD700; color: #000; font-weight:bold;}
.stTextInput>div>input, .stNumberInput>div>input {background-color: #2b2b2b; color:#f0f0f0;}
.stRadio>div {background-color: #2b2b2b; color:#f0f0f0; padding:10px; border-radius:5px;}
</style>
""", unsafe_allow_html=True)

# ------------------ PDF Function ------------------
def generate_pdf(weight, height, age, gender, bmi, category, risk, ideal_min, ideal_max,
                 bmr, activity_level, daily_calories, body_fat, water_intake, protein):
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
        ['Weight', f'{weight} kg ({round(weight*2.20462,1)} lbs)'],
        ['Height', f'{height} cm ({round(height*0.393701,1)} in)'],
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
        "Do 150 min/week moderate exercise",
        "Monitor BMI and body fat regularly",
        "Get 7-9 hours of sleep per night",
        "Manage stress through mindfulness"
    ]
    for tip in tips:
        story.append(Paragraph(f"• {tip}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("🦇 Thank You! Built by Faizan Shah Khan", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ------------------ Inputs ------------------
st.markdown("<h1 style='text-align:center'>🦇 Modern BMI & BMR Dashboard</h1>", unsafe_allow_html=True)
st.write("---")

weight = st.number_input("Weight (kg):", min_value=20.0, max_value=200.0, value=70.0)
height_cm = st.number_input("Height (cm):", min_value=100.0, max_value=220.0, value=170.0)
age = st.number_input("Age (years):", min_value=5, max_value=100, value=25)
gender = st.selectbox("Gender:", ["Male","Female","Other"])
activity_level = st.radio("Activity Level:", ["Sedentary","Light","Moderate","Very Active","Extra Active"])

# ------------------ Calculations ------------------
height_m = height_cm/100
bmi = round(weight/(height_m**2),1)
ideal_min = round(18.5*(height_m**2),1)
ideal_max = round(24.9*(height_m**2),1)

if bmi<18.5:
    category="Underweight"
    risk="Higher risk of nutritional deficiency, osteoporosis"
elif bmi<25:
    category="Normal"
    risk="Low risk, maintain healthy lifestyle"
elif bmi<30:
    category="Overweight"
    risk="Increased risk of heart disease, diabetes"
else:
    category="Obese"
    risk="High risk of heart disease, diabetes, other health issues"

if gender=="Male":
    bmr=88.362 + (13.397*weight) + (4.799*height_cm) - (5.677*age)
elif gender=="Female":
    bmr=447.593 + (9.247*weight) + (3.098*height_cm) - (4.330*age)
else:
    bmr_m=88.362 + (13.397*weight) + (4.799*height_cm) - (5.677*age)
    bmr_f=447.593 + (9.247*weight) + (3.098*height_cm) - (4.330*age)
    bmr=(bmr_m+bmr_f)/2

activity_multipliers={"Sedentary":1.2,"Light":1.375,"Moderate":1.55,"Very Active":1.725,"Extra Active":1.9}
daily_calories = round(bmr*activity_multipliers[activity_level])

if gender=="Male":
    body_fat=round((1.20*bmi)+(0.23*age)-16.2,1)
else:
    body_fat=round((1.20*bmi)+(0.23*age)-5.4,1)
body_fat = max(0,min(60,body_fat))
water_intake=round(weight*35)
protein=round(weight*0.8)

# ------------------ Display Metrics ------------------
st.markdown(f"*BMI:* {bmi} ({category}) | *Health Risk:* {risk}")
st.markdown(f"*Ideal Weight:* {ideal_min}-{ideal_max} kg | {round(ideal_min*2.20462,1)}-{round(ideal_max*2.20462,1)} lbs")
st.markdown(f"*BMR:* {round(bmr)} kcal/day | *Calories Needed:* {daily_calories} kcal/day")
st.markdown(f"*Body Fat:* {body_fat}% | *Water:* {water_intake} ml | *Protein:* {protein} g")

# ------------------ Gauges ------------------
col1,col2 = st.columns(2)

with col1:
    fig_bmi = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bmi,
        title={'text':"BMI"},
        gauge={'axis':{'range':[10,50]},
               'bar':{'color':'yellow'},
               'steps':[{'range':[10,18.5],'color':'blue'},{'range':[18.5,24.9],'color':'green'},{'range':[25,29.9],'color':'orange'},{'range':[30,50],'color':'red'}]}
    ))
    fig_bmi.update_layout(height=350)
    st.plotly_chart(fig_bmi,use_container_width=True)

with col2:
    fig_bmr = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bmr,
        title={'text':"BMR (kcal/day)"},
        gauge={'axis':{'range':[1000,4000]},
               'bar':{'color':'yellow'},
               'steps':[{'range':[1000,1500],'color':'blue'},{'range':[1500,2500],'color':'green'},{'range':[2500,3500],'color':'orange'},{'range':[3500,4000],'color':'red'}]}
    ))
    fig_bmr.update_layout(height=350)
    st.plotly_chart(fig_bmr,use_container_width=True)


# ------------------ PDF Download ------------------
pdf_buffer = generate_pdf(weight,height_cm,age,gender,bmi,category,risk,ideal_min,ideal_max,bmr,activity_level,daily_calories,body_fat,water_intake,protein)
st.download_button("📄 Download PDF Report", data=pdf_buffer, file_name=f"BMI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf")

# ------------------ Health Tips ------------------
st.markdown("### 🦇 Health Tips & Recommendations")
tips = [
    "Maintain a balanced diet with proper calories",
    "Stay hydrated (30-40 ml/kg body weight)",
    "Do 150 min/week moderate exercise",
    "Monitor BMI and body fat regularly",
    "Get 7-9 hours of sleep per night",
    "Manage stress through mindfulness"
]
for tip in tips:
    st.markdown(f"• {tip}")

st.markdown("<h2 style='text-align:center'>🦇 Thank You! Built by Faizan Shah Khan</h2>", unsafe_allow_html=True)
