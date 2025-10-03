import streamlit as st
import pandas as pd

# Set up the Streamlit app title
st.title("Body Mass Index (BMI) Calculator & Tracker")

# 1. Establish the connection using the name defined in the Secrets file
# The type='sql' tells Streamlit to use a standard SQL connection
conn = st.connection('bmi_db', type='sql')

def init_db():
    """
    Function to ensure the bmi_records table exists.
    This query will only create the table if it does NOT already exist.
    """
    try:
        with conn.session as s:
            # Note: We use the MySQL data types here. Adjust if using PostgreSQL, etc.
            s.execute("""
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    weight_kg DECIMAL(5, 2) NOT NULL,
                    height_m DECIMAL(4, 2) NOT NULL,
                    bmi_value DECIMAL(4, 2) NOT NULL,
                    category VARCHAR(50),
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP 
                );
            """)
            s.commit()
    except Exception as e:
        st.error(f"Error initializing database: {e}")

# Run the initialization function once at the start of the app
init_db()


# --- User Input & Calculation Logic ---

st.header("Calculate Your BMI")

with st.form("bmi_form"):
    # Input for weight (kg)
    weight_kg = st.number_input("Enter Weight (kg)", min_value=1.0, value=70.0, step=0.1)
    
    # Input for height in meters (assuming user will input cm and we convert)
    height_cm = st.number_input("Enter Height (cm)", min_value=50.0, value=170.0, step=0.1)
    
    submitted = st.form_submit_button("Calculate & Save BMI")

if submitted:
    height_m = height_cm / 100.0  # Convert cm to meters
    
    if height_m <= 0:
        st.error("Height must be greater than zero.")
    else:
        # Calculate BMI
        bmi = weight_kg / (height_m ** 2)
        
        # Determine BMI category
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal Weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obesity"
            
        st.success(f"Your BMI is: *{round(bmi, 2)}* ({category})")
        
        # 2. Insert the calculated BMI into the database
        try:
            with conn.session as s:
                s.execute(
                    """
                    INSERT INTO bmi_records (weight_kg, height_m, bmi_value, category) 
                    VALUES (:w, :h, :b, :c)
                    """,
                    params={
                        "w": round(weight_kg, 2), 
                        "h": round(height_m, 2), 
                        "b": round(bmi, 2), 
                        "c": category
                    }
                )
                s.commit()
                st.toast("BMI record saved successfully!")
        except Exception as e:
            st.error(f"Failed to save data: {e}")


# --- Display Past Records ---

st.header("Past BMI Records")

# 3. Query the data from the database
# ttl=60 caches the result for 60 seconds to reduce database load
try:
    df = conn.query("SELECT * FROM bmi_records ORDER BY timestamp DESC", ttl=60)
    
    if df.empty:
        st.info("No records found yet. Calculate your BMI above to save the first one!")
    else:
        # Rename columns for better display
        df.columns = ["ID", "Weight (kg)", "Height (m)", "BMI Value", "Category", "Timestamp"]
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.warning(f"Could not retrieve records. Check your database connection: {e}")
