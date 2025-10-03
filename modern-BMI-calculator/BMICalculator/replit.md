# BMI Calculator Dashboard

## Overview

A Streamlit-based BMI (Body Mass Index) calculator with health tracking capabilities. The application allows users to calculate their BMI based on weight, height, age, and gender inputs, categorizes the results, provides health risk assessments, and stores calculation history in a PostgreSQL database. The system generates visual dashboards and PDF reports for health tracking.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
**Framework**: Streamlit web framework for Python
- **Decision**: Use Streamlit for rapid UI development with minimal frontend code
- **Rationale**: Streamlit provides built-in widgets (sliders, selectboxes) and easy state management, perfect for data-focused applications
- **Layout**: Wide layout with columnar design for responsive input forms
- **Visualization**: Plotly for interactive BMI charts and gauges

### Backend Architecture
**Language**: Python 3.x
- **Application Structure**: Single-file monolithic architecture (app.py)
- **Decision**: Keep all logic in one file for simplicity given the application scope
- **Core Modules**:
  - BMI calculation engine (mathematical formula: weight/height²)
  - Health categorization logic (Underweight/Normal/Overweight/Obese)
  - Risk assessment system based on BMI ranges
  - PDF report generation using ReportLab

### Data Storage
**Database**: PostgreSQL
- **Connection**: Environment variable-based connection string (DATABASE_URL)
- **Table Schema**: `bmi_history` table storing:
  - weight (numeric)
  - height (numeric)
  - age (integer)
  - gender (text)
  - bmi (calculated numeric)
  - created_at (timestamp)
- **Decision**: Use PostgreSQL for reliable relational data storage with ACID compliance
- **Query Patterns**: Simple INSERT for saving records, SELECT with ORDER BY and LIMIT for history retrieval

### Health Logic & Calculations
**BMI Categories** (WHO standards):
- Underweight: BMI < 18.5
- Normal: BMI 18.5-24.9
- Overweight: BMI 25-29.9
- Obese: BMI ≥ 30

**Color-coded Risk System**:
- Blue (Underweight): Nutritional deficiency risk
- Green (Normal): Low risk
- Orange (Overweight): Cardiovascular/diabetes risk
- Red (Obese): High disease risk

### Report Generation
**Library**: ReportLab
- **Format**: PDF generation with letter page size
- **Components**: Structured reports with paragraphs, tables, and styling
- **Output**: In-memory BytesIO streams for download without file system storage
- **Decision**: Use ReportLab for professional PDF output with precise layout control

## External Dependencies

### Python Libraries
- **streamlit**: Core web framework for UI and interactions
- **PIL (Pillow)**: Image processing (likely for logos or graphics)
- **plotly**: Interactive data visualization and charts
- **psycopg2**: PostgreSQL database adapter
- **reportlab**: PDF document generation

### Database
- **PostgreSQL**: Primary data persistence layer
  - Connection via DATABASE_URL environment variable
  - Stores historical BMI calculations
  - Table: `bmi_history` (schema defined in architecture section)

### Environment Configuration
- **DATABASE_URL**: PostgreSQL connection string (required)
- Deployment assumes environment variable availability (Replit Secrets or similar)

### Design Patterns
- **Repository Pattern**: Database operations encapsulated in dedicated functions (get_db_connection, save_bmi_record, get_bmi_history)
- **Error Handling**: Try-except blocks around database operations with user-friendly error messages
- **Resource Management**: Explicit connection and cursor cleanup (close operations)