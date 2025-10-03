import streamlit as st
from PIL import Image
import plotly.graph_objects as go
import psycopg2
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO

# Page config
st.set_page_config(
    page_title="BMI Calculator Dashboard",
    page_icon="🏋",
    layout="wide"
)

# Database connection functions
def get_db_connection():
    """Create and return a database connection"""
    return psycopg2.connect(os.environ['DATABASE_URL'])

def save_bmi_record(weight, height, age, gender, bmi):
    """Save BMI record to database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bmi_history (weight, height, age, gender, bmi) VALUES (%s, %s, %s, %s, %s)",
            (weight, height, age, gender, bmi)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving to database: {e}")
        return False

def get_bmi_history():
    """Retrieve BMI history from database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT weight, height, age, gender, bmi, created_at FROM bmi_history ORDER BY created_at DESC LIMIT 50")
        records = cur.fetchall()
        cur.close()
        conn.close()
        return records
    except Exception as e:
        st.error(f"Error retrieving history: {e}")
        return []

def generate_pdf_report(weight, height, age, gender, bmi, category, risk, ideal_min, ideal_max, 
                        daily_calories, activity_level, body_fat, water_intake, protein, bmr, activity_mult):
    """Generate a PDF report with BMI data"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E90FF'),
        spaceAfter=30,
        alignment=1
    )
    story.append(Paragraph("BMI Calculator & Health Dashboard", title_style))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # BMI Results Section
    story.append(Paragraph("<b>Your BMI Results</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E90FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(bmi_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Recommendations Section
    story.append(Paragraph("<b>Personalized Recommendations</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    rec_data = [
        ['Recommendation', 'Value'],
        ['Ideal Weight Range', f'{ideal_min} - {ideal_max} kg'],
        ['Activity Level', activity_level],
        ['Basal Metabolic Rate (BMR)', f'{round(bmr)} kcal/day'],
        ['Activity Multiplier', f'{activity_mult}x'],
        ['Daily Calorie Intake', f'{daily_calories} kcal/day'],
        ['Estimated Body Fat', f'{body_fat}%'],
        ['Daily Water Intake', f'{water_intake} ml'],
        ['Daily Protein Need', f'{protein} g'],
    ]
    
    rec_table = Table(rec_data, colWidths=[3*inch, 3*inch])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E90FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Health Tips Section
    story.append(Paragraph("<b>Personalized Health Tips</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    if category == "Underweight":
        tips_text = """• Increase caloric intake with nutrient-dense foods<br/>
        • Add healthy fats like nuts, avocados, and olive oil<br/>
        • Strength training to build muscle mass<br/>
        • Eat frequent smaller meals throughout the day<br/>
        • Consult a nutritionist for a personalized meal plan"""
    elif category == "Normal":
        tips_text = """• Maintain your current lifestyle - you're doing great!<br/>
        • Continue balanced diet with variety of nutrients<br/>
        • Stay active with at least 150 minutes of moderate exercise per week<br/>
        • Monitor your BMI regularly to maintain this healthy range<br/>
        • Stay hydrated and get adequate sleep"""
    elif category == "Overweight":
        tips_text = """• Create a moderate calorie deficit (300-500 calories/day)<br/>
        • Increase physical activity - aim for 300 minutes per week<br/>
        • Focus on whole foods and reduce processed foods<br/>
        • Practice portion control and mindful eating<br/>
        • Consider strength training to preserve muscle mass"""
    else:
        tips_text = """• Consult healthcare professional for personalized guidance<br/>
        • Start with small changes - gradual weight loss is sustainable<br/>
        • Increase daily movement even if just walking<br/>
        • Focus on nutrition quality over restriction<br/>
        • Consider professional support from dietitian or trainer"""
    
    story.append(Paragraph(tips_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Paragraph("Created by Faizan Shah Khan | Interactive BMI Tool", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ------------------ Front Page ------------------
st.markdown("<h1 style='text-align: center; color: #1E90FF;'>🏋 BMI Calculator & Health Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Interactive BMI tool with health advice and daily calorie recommendation</p>", unsafe_allow_html=True)
st.write("---")

# ------------------ Input Section ------------------
col1, col2 = st.columns(2)

with col1:
    weight = st.slider("Select your weight (kg):", 20, 200, 70)
with col2:
    height_cm = st.slider("Select your height (cm):", 100, 220, 170)

age = st.slider("Age:", 5, 100, 25)
gender = st.selectbox("Gender:", ["Male", "Female", "Other"])

st.markdown("### Activity Level")
activity_level = st.select_slider(
    "Select your activity level:",
    options=["Sedentary", "Light", "Moderate", "Very Active", "Extra Active"],
    value="Moderate",
    help="Sedentary: Little/no exercise | Light: 1-3 days/week | Moderate: 3-5 days/week | Very Active: 6-7 days/week | Extra Active: Very hard exercise + physical job"
)

# ------------------ BMI Calculation ------------------
height_m = height_cm / 100
bmi = round(weight / (height_m ** 2), 1)

# BMI Category & Health Risk
if bmi < 18.5:
    category = "Underweight"
    color = "blue"
    risk = "Higher risk of nutritional deficiency and osteoporosis."
elif 18.5 <= bmi < 24.9:
    category = "Normal"
    color = "green"
    risk = "Low risk, maintain a healthy lifestyle."
elif 25 <= bmi < 29.9:
    category = "Overweight"
    color = "orange"
    risk = "Increased risk of cardiovascular disease and diabetes."
else:
    category = "Obese"
    color = "red"
    risk = "High risk of heart disease, diabetes, and other health issues."

# Ideal weight range
ideal_weight_min = round(18.5 * (height_m ** 2), 1)
ideal_weight_max = round(24.9 * (height_m ** 2), 1)

# Daily calories recommendation based on more accurate formula
# Using Harris-Benedict Equation for BMR calculation
if gender == "Male":
    bmr = 88.362 + (13.397 * weight) + (4.799 * height_cm) - (5.677 * age)
elif gender == "Female":
    bmr = 447.593 + (9.247 * weight) + (3.098 * height_cm) - (4.330 * age)
else:
    # Average of male and female calculations for "Other"
    bmr_male = 88.362 + (13.397 * weight) + (4.799 * height_cm) - (5.677 * age)
    bmr_female = 447.593 + (9.247 * weight) + (3.098 * height_cm) - (4.330 * age)
    bmr = (bmr_male + bmr_female) / 2

# Activity level multipliers
activity_multipliers = {
    "Sedentary": 1.2,
    "Light": 1.375,
    "Moderate": 1.55,
    "Very Active": 1.725,
    "Extra Active": 1.9
}

# Calculate daily calories based on activity level
daily_calories = round(bmr * activity_multipliers[activity_level])

# ------------------ Display Results ------------------
st.markdown("<h2 style='color:#1E90FF;'>Your BMI Results</h2>", unsafe_allow_html=True)

col3, col4 = st.columns([2,3])

with col3:
    st.metric("BMI Value", f"{bmi} ({category})")
    st.info(f"Health Risk: {risk}")
    st.write(f"Ideal Weight: {ideal_weight_min} kg - {ideal_weight_max} kg")
    st.write(f"Activity Level: **{activity_level}**")
    st.write(f"Recommended Daily Calories: **{daily_calories} kcal/day**")
    st.caption(f"Based on BMR ({round(bmr)} kcal) × {activity_multipliers[activity_level]} activity factor")

with col4:
    # Color-coded gauge for BMI
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
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 25
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# ------------------ BMI Comparison Chart ------------------
st.markdown("<h3 style='color:#1E90FF;'>BMI Range Comparison</h3>", unsafe_allow_html=True)

# Create horizontal bar chart showing BMI ranges
fig_comparison = go.Figure()

# Add BMI range bars
categories_ranges = [
    ("Underweight", 10, 18.5, "lightblue"),
    ("Normal Weight", 18.5, 24.9, "lightgreen"),
    ("Overweight", 25, 29.9, "#FFE4B5"),
    ("Obese", 30, 40, "lightcoral")
]

for cat, start, end, color_bar in categories_ranges:
    fig_comparison.add_trace(go.Bar(
        name=cat,
        x=[end - start],
        y=[cat],
        orientation='h',
        marker=dict(color=color_bar),
        text=f"{start} - {end}",
        textposition='inside',
        base=start,
        hovertemplate=f"{cat}<br>Range: {start} - {end}<br><extra></extra>"
    ))

# Map category to display label
category_display_map = {
    "Underweight": "Underweight",
    "Normal": "Normal Weight",
    "Overweight": "Overweight",
    "Obese": "Obese"
}
display_category = category_display_map.get(category, category)

# Add user's current BMI as a marker
fig_comparison.add_trace(go.Scatter(
    x=[bmi],
    y=[display_category],
    mode='markers+text',
    marker=dict(
        color='red',
        size=20,
        symbol='diamond',
        line=dict(color='darkred', width=2)
    ),
    text=f"You: {bmi}",
    textposition="top center",
    textfont=dict(size=14, color='darkred', family='Arial Black'),
    name='Your BMI',
    hovertemplate=f"Your BMI: {bmi}<extra></extra>"
))

fig_comparison.update_layout(
    title="Where You Stand",
    xaxis_title="BMI Value",
    yaxis_title="",
    showlegend=False,
    height=300,
    xaxis=dict(range=[10, 40]),
    barmode='overlay'
)

st.plotly_chart(fig_comparison, use_container_width=True)

# ------------------ Save to History Button ------------------
st.markdown("---")
col_save, col_pdf = st.columns(2)

with col_save:
    if st.button("💾 Save Current BMI to History", type="primary", use_container_width=True):
        if save_bmi_record(weight, height_cm, age, gender, bmi):
            st.success("✅ BMI record saved successfully!")
            st.rerun()

with col_pdf:
    # Calculate body fat for PDF (same formula used later, clamped to 0-60%)
    if gender == "Male":
        body_fat_pdf = (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        body_fat_pdf = (1.20 * bmi) + (0.23 * age) - 5.4
    body_fat_pdf = max(0, min(60, round(body_fat_pdf, 1)))
    
    water_intake_pdf = round(weight * 35)
    protein_requirement_pdf = round(weight * 0.8)
    
    pdf_buffer = generate_pdf_report(
        weight, height_cm, age, gender, bmi, category, risk,
        ideal_weight_min, ideal_weight_max, daily_calories, activity_level,
        body_fat_pdf, water_intake_pdf, protein_requirement_pdf, bmr, activity_multipliers[activity_level]
    )
    
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_buffer,
        file_name=f"BMI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# ------------------ Additional Health Metrics ------------------
st.markdown("<h3 style='color:#1E90FF;'>Additional Health Metrics</h3>", unsafe_allow_html=True)

col5, col6, col7, col8 = st.columns(4)

with col5:
    # Body Fat Percentage (rough estimation)
    if gender == "Male":
        body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
    # Clamp body fat to realistic range (0-60%)
    body_fat = max(0, min(60, round(body_fat, 1)))
    st.metric("Estimated Body Fat %", f"{body_fat}%")

with col6:
    # Muscle Mass Estimation
    # Calculate lean body mass first
    lean_body_mass = weight * (1 - body_fat / 100)
    
    # Estimate muscle mass (typically 40-50% of lean body mass depending on fitness level)
    # Adjust based on BMI category and gender
    if gender == "Male":
        muscle_multiplier = 0.45 if bmi >= 25 else 0.50  # Lower multiplier for higher BMI
    else:
        muscle_multiplier = 0.40 if bmi >= 25 else 0.45
    
    muscle_mass = max(0, round(lean_body_mass * muscle_multiplier, 1))
    st.metric("Estimated Muscle Mass", f"{muscle_mass} kg")

with col7:
    # Water intake recommendation (ml per day)
    water_intake = round(weight * 35)
    st.metric("Daily Water Intake", f"{water_intake} ml")

with col8:
    # Protein requirement (grams per day)
    protein_requirement = round(weight * 0.8)
    st.metric("Daily Protein Need", f"{protein_requirement} g")

# ------------------ BMI Progress Tracking ------------------
st.markdown("<h3 style='color:#1E90FF;'>BMI Categories Reference</h3>", unsafe_allow_html=True)

# Create a reference chart
categories_data = {
    'Category': ['Underweight', 'Normal', 'Overweight', 'Obese'],
    'BMI Range': ['< 18.5', '18.5 - 24.9', '25.0 - 29.9', '≥ 30.0'],
    'Health Risk': ['Nutritional deficiency', 'Low risk', 'Moderate risk', 'High risk']
}

import pandas as pd
df = pd.DataFrame(categories_data)
st.table(df)

# ------------------ BMI History and Progress Tracking ------------------
st.markdown("<h3 style='color:#1E90FF;'>📈 Your BMI Progress Over Time</h3>", unsafe_allow_html=True)

history = get_bmi_history()
if history and len(history) > 0:
    # Convert to DataFrame for easier plotting
    history_df = pd.DataFrame(history, columns=['Weight', 'Height', 'Age', 'Gender', 'BMI', 'Date'])
    history_df = history_df.sort_values('Date')
    
    # Create line chart for BMI progress
    fig_progress = go.Figure()
    fig_progress.add_trace(go.Scatter(
        x=history_df['Date'],
        y=history_df['BMI'],
        mode='lines+markers',
        name='BMI',
        line=dict(color='#1E90FF', width=3),
        marker=dict(size=8)
    ))
    
    # Add reference lines for BMI categories
    fig_progress.add_hline(y=18.5, line_dash="dash", line_color="blue", annotation_text="Underweight")
    fig_progress.add_hline(y=25, line_dash="dash", line_color="orange", annotation_text="Overweight")
    fig_progress.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Obese")
    
    # Add shaded regions for BMI categories
    fig_progress.add_hrect(y0=18.5, y1=24.9, fillcolor="green", opacity=0.1, line_width=0)
    
    fig_progress.update_layout(
        title="BMI Trend Over Time",
        xaxis_title="Date",
        yaxis_title="BMI",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_progress, use_container_width=True)
    
    # Display recent records in a table
    st.markdown("**Recent BMI Records:**")
    display_df = history_df[['Date', 'Weight', 'Height', 'BMI']].head(10)
    display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d %H:%M')
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("No BMI history yet. Save your current BMI to start tracking your progress!")

# ------------------ Tips Section ------------------
st.markdown("<h3 style='color:#1E90FF;'>Personalized Health Tips</h3>", unsafe_allow_html=True)

if category == "Underweight":
    tips = """
    - **Increase caloric intake** with nutrient-dense foods
    - **Add healthy fats** like nuts, avocados, and olive oil
    - **Strength training** to build muscle mass
    - **Eat frequent smaller meals** throughout the day
    - **Consult a nutritionist** for a personalized meal plan
    """
elif category == "Normal":
    tips = """
    - **Maintain your current lifestyle** - you're doing great!
    - **Continue balanced diet** with variety of nutrients
    - **Stay active** with at least 150 minutes of moderate exercise per week
    - **Monitor your BMI** regularly to maintain this healthy range
    - **Stay hydrated** and get adequate sleep
    """
elif category == "Overweight":
    tips = """
    - **Create a moderate calorie deficit** (300-500 calories/day)
    - **Increase physical activity** - aim for 300 minutes per week
    - **Focus on whole foods** and reduce processed foods
    - **Practice portion control** and mindful eating
    - **Consider strength training** to preserve muscle mass
    """
else:  # Obese
    tips = """
    - **Consult healthcare professional** for personalized guidance
    - **Start with small changes** - gradual weight loss is sustainable
    - **Increase daily movement** even if just walking
    - **Focus on nutrition quality** over restriction
    - **Consider professional support** from dietitian or trainer
    """

st.markdown(tips)

# ------------------ General Health Tips ------------------
st.markdown("<h4 style='color:#1E90FF;'>General Health Guidelines</h4>", unsafe_allow_html=True)
st.markdown("""
- **Sleep**: Aim for 7-9 hours of quality sleep per night
- **Hydration**: Drink water regularly throughout the day
- **Exercise**: Mix cardio and strength training for optimal health
- **Stress Management**: Practice relaxation techniques like meditation
- **Regular Check-ups**: Monitor your health with regular medical visits
""")

st.write("---")
st.markdown("<p style='text-align:center; font-size:14px;'>Created by Faizan Shah Khan | Interactive BMI Tool</p>", unsafe_allow_html=True)
