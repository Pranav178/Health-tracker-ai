import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

def validate_health_data(data):
    """Validate health data input"""
    errors = []
    
    # Weight validation
    if 'weight' in data and data['weight'] is not None:
        if data['weight'] <= 0 or data['weight'] > 500:
            errors.append("Weight must be between 1 and 500 kg")
    
    # Blood pressure validation
    if 'blood_pressure_systolic' in data and data['blood_pressure_systolic'] is not None:
        if data['blood_pressure_systolic'] < 70 or data['blood_pressure_systolic'] > 300:
            errors.append("Systolic blood pressure must be between 70 and 300 mmHg")
    
    if 'blood_pressure_diastolic' in data and data['blood_pressure_diastolic'] is not None:
        if data['blood_pressure_diastolic'] < 40 or data['blood_pressure_diastolic'] > 200:
            errors.append("Diastolic blood pressure must be between 40 and 200 mmHg")
    
    # Heart rate validation
    if 'heart_rate' in data and data['heart_rate'] is not None:
        if data['heart_rate'] < 30 or data['heart_rate'] > 220:
            errors.append("Heart rate must be between 30 and 220 bpm")
    
    # Sleep hours validation
    if 'sleep_hours' in data and data['sleep_hours'] is not None:
        if data['sleep_hours'] < 0 or data['sleep_hours'] > 24:
            errors.append("Sleep hours must be between 0 and 24")
    
    # Exercise minutes validation
    if 'exercise_minutes' in data and data['exercise_minutes'] is not None:
        if data['exercise_minutes'] < 0 or data['exercise_minutes'] > 1440:
            errors.append("Exercise minutes must be between 0 and 1440 (24 hours)")
    
    return errors

def format_health_tip(tip_type):
    """Get formatted health tips"""
    tips = {
        'weight': "💡 **Weight Management Tip**: Track your weight at the same time each day, preferably in the morning after using the bathroom.",
        'blood_pressure': "💡 **Blood Pressure Tip**: Take measurements at the same time daily, avoid caffeine 30 minutes before, and rest for 5 minutes beforehand.",
        'heart_rate': "💡 **Heart Rate Tip**: Resting heart rate is best measured first thing in the morning. Lower resting heart rate often indicates better fitness.",
        'sleep': "💡 **Sleep Tip**: Aim for 7-9 hours of quality sleep. Maintain consistent sleep and wake times, even on weekends.",
        'exercise': "💡 **Exercise Tip**: WHO recommends at least 150 minutes of moderate-intensity exercise per week. Start small and gradually increase.",
        'mood': "💡 **Mood Tip**: Regular exercise, adequate sleep, and social connections significantly impact mood and mental health."
    }
    return tips.get(tip_type, "💡 **Health Tip**: Consistency in tracking helps identify patterns and improve your health journey.")

def calculate_bmi(weight, height):
    """Calculate BMI"""
    if weight and height and height > 0:
        bmi = weight / (height ** 2)
        return round(bmi, 1)
    return None

def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi is None:
        return "Unknown"
    elif bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def get_blood_pressure_category(systolic, diastolic):
    """Get blood pressure category"""
    if systolic is None or diastolic is None:
        return "Unknown"
    elif systolic < 120 and diastolic < 80:
        return "Normal"
    elif systolic < 130 and diastolic < 80:
        return "Elevated"
    elif systolic < 140 or diastolic < 90:
        return "High Blood Pressure Stage 1"
    elif systolic < 180 or diastolic < 120:
        return "High Blood Pressure Stage 2"
    else:
        return "Hypertensive Crisis"

def get_heart_rate_category(heart_rate, age=None):
    """Get heart rate category"""
    if heart_rate is None:
        return "Unknown"
    elif heart_rate < 60:
        return "Below Normal (Bradycardia)"
    elif heart_rate <= 100:
        return "Normal"
    else:
        return "Above Normal (Tachycardia)"

def create_metric_card(title, value, delta=None, help_text=None):
    """Create a metric card with optional delta and help text"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if delta is not None:
            st.metric(title, value, delta=delta, help=help_text)
        else:
            st.metric(title, value, help=help_text)
    
    if help_text:
        with col2:
            st.help(help_text)

def format_date_range(start_date, end_date):
    """Format date range for display"""
    if start_date and end_date:
        return f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
    return "No date range specified"

def get_health_score(health_data):
    """Calculate overall health score based on recent data"""
    if health_data.empty:
        return 0, "No data available"
    
    recent_data = health_data.tail(7)  # Last 7 entries
    score = 0
    factors = []
    
    # Weight stability (if tracked)
    if 'weight' in recent_data.columns and len(recent_data['weight'].dropna()) > 1:
        weight_data = recent_data['weight'].dropna()
        weight_std = weight_data.std()
        if weight_std < 1:  # Less than 1kg variation
            score += 20
            factors.append("Weight stability")
    
    # Blood pressure
    if 'blood_pressure_systolic' in recent_data.columns and 'blood_pressure_diastolic' in recent_data.columns:
        systolic = recent_data['blood_pressure_systolic'].mean()
        diastolic = recent_data['blood_pressure_diastolic'].mean()
        if systolic < 120 and diastolic < 80:
            score += 25
            factors.append("Good blood pressure")
        elif systolic < 140 and diastolic < 90:
            score += 15
            factors.append("Acceptable blood pressure")
    
    # Heart rate
    if 'heart_rate' in recent_data.columns:
        avg_hr = recent_data['heart_rate'].mean()
        if 60 <= avg_hr <= 100:
            score += 20
            factors.append("Normal heart rate")
    
    # Sleep
    if 'sleep_hours' in recent_data.columns:
        avg_sleep = recent_data['sleep_hours'].mean()
        if 7 <= avg_sleep <= 9:
            score += 20
            factors.append("Adequate sleep")
        elif 6 <= avg_sleep <= 10:
            score += 10
            factors.append("Reasonable sleep")
    
    # Exercise
    if 'exercise_minutes' in recent_data.columns:
        total_exercise = recent_data['exercise_minutes'].sum()
        if total_exercise >= 150:  # WHO recommendation per week
            score += 15
            factors.append("Sufficient exercise")
        elif total_exercise >= 75:
            score += 10
            factors.append("Some exercise")
    
    return min(score, 100), factors

def show_info_box(title, content, icon="ℹ️"):
    """Show an information box"""
    st.info(f"{icon} **{title}**\n\n{content}")

def show_success_message(message):
    """Show success message"""
    st.success(f"✅ {message}")

def show_warning_message(message):
    """Show warning message"""
    st.warning(f"⚠️ {message}")

def show_error_message(message):
    """Show error message"""
    st.error(f"❌ {message}")
