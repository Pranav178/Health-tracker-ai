import streamlit as st
from datetime import datetime, date
import pandas as pd
from utils import validate_health_data, format_health_tip, show_success_message, show_error_message

def show_data_entry():
    """Display the data entry page for health metrics"""
    st.title("📝 Health Data Entry")
    st.markdown("Log your daily health metrics to track your progress over time.")
    
    # Get database manager from session state
    database_manager = st.session_state.database_manager
    
    # Check if there's data for today
    today = date.today()
    existing_data = database_manager.get_health_data(1)  # Get today's data
    
    today_entry = None
    if not existing_data.empty:
        today_entries = existing_data[existing_data['date'] == today.strftime('%Y-%m-%d')]
        if not today_entries.empty:
            today_entry = today_entries.iloc[0].to_dict()
    
    if today_entry:
        st.info(f"📅 You already have an entry for today ({today.strftime('%Y-%m-%d')}). You can update it below.")
    
    # Data entry form
    with st.form("health_data_form"):
        st.subheader("📅 Basic Information")
        
        # Date selection
        entry_date = st.date_input(
            "Date",
            value=today,
            max_value=today,
            help="Select the date for this health entry"
        )
        
        # Physical Metrics Section
        st.subheader("⚖️ Physical Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input(
                "Weight (kg)",
                min_value=0.0,
                max_value=500.0,
                value=float(today_entry.get('weight', 0.0)) if today_entry and pd.notna(today_entry.get('weight')) else 0.0,
                step=0.1,
                help="Enter your weight in kilograms"
            )
            
            sleep_hours = st.number_input(
                "Sleep Hours",
                min_value=0.0,
                max_value=24.0,
                value=float(today_entry.get('sleep_hours', 0.0)) if today_entry and pd.notna(today_entry.get('sleep_hours')) else 0.0,
                step=0.5,
                help="How many hours did you sleep?"
            )
        
        with col2:
            exercise_minutes = st.number_input(
                "Exercise Minutes",
                min_value=0,
                max_value=1440,
                value=int(today_entry.get('exercise_minutes', 0)) if today_entry and pd.notna(today_entry.get('exercise_minutes')) else 0,
                step=5,
                help="Total minutes of exercise today"
            )
        
        # Vital Signs Section
        st.subheader("❤️ Vital Signs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            bp_systolic = st.number_input(
                "Blood Pressure - Systolic (mmHg)",
                min_value=0,
                max_value=300,
                value=int(today_entry.get('blood_pressure_systolic', 0)) if today_entry and pd.notna(today_entry.get('blood_pressure_systolic')) else 0,
                help="Top number of blood pressure reading"
            )
            
            bp_diastolic = st.number_input(
                "Blood Pressure - Diastolic (mmHg)",
                min_value=0,
                max_value=200,
                value=int(today_entry.get('blood_pressure_diastolic', 0)) if today_entry and pd.notna(today_entry.get('blood_pressure_diastolic')) else 0,
                help="Bottom number of blood pressure reading"
            )
        
        with col2:
            heart_rate = st.number_input(
                "Heart Rate (bpm)",
                min_value=0,
                max_value=220,
                value=int(today_entry.get('heart_rate', 0)) if today_entry and pd.notna(today_entry.get('heart_rate')) else 0,
                help="Resting heart rate in beats per minute"
            )
        
        # Wellness Section
        st.subheader("😊 Wellness & Mood")
        
        mood_options = ["Excellent", "Good", "Average", "Poor", "Very Poor"]
        mood = st.selectbox(
            "Mood",
            mood_options,
            index=mood_options.index(today_entry.get('mood', 'Average')) if today_entry and today_entry.get('mood') in mood_options else 2,
            help="How are you feeling today?"
        )
        
        symptoms = st.text_area(
            "Symptoms (optional)",
            value=today_entry.get('symptoms', '') if today_entry else '',
            placeholder="Any symptoms you experienced today (headache, fatigue, etc.)",
            help="Note any symptoms or health concerns"
        )
        
        notes = st.text_area(
            "Additional Notes (optional)",
            value=today_entry.get('notes', '') if today_entry else '',
            placeholder="Any additional notes about your health today",
            help="Any additional observations or notes"
        )
        
        # Submit button
        submitted = st.form_submit_button("💾 Save Health Data", use_container_width=True)
        
        if submitted:
            # Prepare data for saving
            health_data = {
                'date': entry_date.strftime('%Y-%m-%d'),
                'weight': weight if weight > 0 else None,
                'blood_pressure_systolic': bp_systolic if bp_systolic > 0 else None,
                'blood_pressure_diastolic': bp_diastolic if bp_diastolic > 0 else None,
                'heart_rate': heart_rate if heart_rate > 0 else None,
                'sleep_hours': sleep_hours if sleep_hours > 0 else None,
                'exercise_minutes': exercise_minutes if exercise_minutes > 0 else None,
                'mood': mood,
                'symptoms': symptoms.strip() if symptoms.strip() else None,
                'notes': notes.strip() if notes.strip() else None
            }
            
            # Validate data
            validation_errors = validate_health_data(health_data)
            
            if validation_errors:
                for error in validation_errors:
                    show_error_message(error)
            else:
                # Save data
                try:
                    success = database_manager.save_health_data(health_data)
                    
                    if success:
                        show_success_message("✅ Health data saved successfully!")
                        st.balloons()
                        
                        # Show summary of saved data
                        st.markdown("### 📊 Saved Data Summary")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if health_data['weight']:
                                st.metric("Weight", f"{health_data['weight']:.1f} kg")
                            if health_data['heart_rate']:
                                st.metric("Heart Rate", f"{health_data['heart_rate']} bpm")
                            if health_data['sleep_hours']:
                                st.metric("Sleep", f"{health_data['sleep_hours']:.1f} hours")
                        
                        with col2:
                            if health_data['blood_pressure_systolic'] and health_data['blood_pressure_diastolic']:
                                st.metric("Blood Pressure", f"{health_data['blood_pressure_systolic']}/{health_data['blood_pressure_diastolic']} mmHg")
                            if health_data['exercise_minutes']:
                                st.metric("Exercise", f"{health_data['exercise_minutes']} minutes")
                            st.metric("Mood", f"{health_data['mood']}")
                        
                        # Provide quick tips based on entered data
                        if health_data['exercise_minutes'] and health_data['exercise_minutes'] >= 30:
                            st.success("🎉 Great job on getting 30+ minutes of exercise!")
                        
                        if health_data['sleep_hours'] and health_data['sleep_hours'] >= 7:
                            st.success("😴 Excellent sleep duration!")
                        
                        if health_data['mood'] in ['Good', 'Excellent']:
                            st.success("😊 It's great that you're feeling positive!")
                        
                        # Quick actions
                        st.markdown("### ⚡ What's Next?")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("📊 View Dashboard", use_container_width=True):
                                st.switch_page("pages/dashboard.py")
                        
                        with col2:
                            if st.button("🤖 Get AI Insights", use_container_width=True):
                                st.switch_page("pages/insights.py")
                        
                        with col3:
                            if st.button("🎯 Manage Goals", use_container_width=True):
                                st.switch_page("pages/goals.py")
                    
                    else:
                        show_error_message("❌ Failed to save health data. Please try again.")
                        
                except Exception as e:
                    show_error_message(f"❌ Error saving data: {str(e)}")
    
    # Quick entry shortcuts
    st.header("⚡ Quick Entry")
    st.markdown("Use these shortcuts for common health metrics:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🏃‍♂️ Exercise Presets**")
        if st.button("30 min Walk", use_container_width=True):
            st.session_state.quick_exercise = 30
        if st.button("60 min Gym", use_container_width=True):
            st.session_state.quick_exercise = 60
        if st.button("90 min Sports", use_container_width=True):
            st.session_state.quick_exercise = 90
    
    with col2:
        st.markdown("**😴 Sleep Presets**")
        if st.button("7 hours", use_container_width=True):
            st.session_state.quick_sleep = 7.0
        if st.button("8 hours", use_container_width=True):
            st.session_state.quick_sleep = 8.0
        if st.button("9 hours", use_container_width=True):
            st.session_state.quick_sleep = 9.0
    
    with col3:
        st.markdown("**😊 Mood Presets**")
        if st.button("Feeling Great!", use_container_width=True):
            st.session_state.quick_mood = "Excellent"
        if st.button("Good Day", use_container_width=True):
            st.session_state.quick_mood = "Good"
        if st.button("Average Day", use_container_width=True):
            st.session_state.quick_mood = "Average"
    
    # Recent entries
    st.header("📅 Recent Entries")
    
    recent_data = database_manager.get_health_data(7)  # Last 7 days
    
    if not recent_data.empty:
        st.subheader("Last 7 Days")
        
        # Format data for display
        display_data = recent_data.copy()
        
        # Format columns for better display
        if 'weight' in display_data.columns:
            display_data['weight'] = display_data['weight'].apply(lambda x: f"{x:.1f} kg" if pd.notna(x) and x > 0 else "")
        
        if 'heart_rate' in display_data.columns:
            display_data['heart_rate'] = display_data['heart_rate'].apply(lambda x: f"{x:.0f} bpm" if pd.notna(x) and x > 0 else "")
        
        if 'sleep_hours' in display_data.columns:
            display_data['sleep_hours'] = display_data['sleep_hours'].apply(lambda x: f"{x:.1f} hrs" if pd.notna(x) and x > 0 else "")
        
        if 'exercise_minutes' in display_data.columns:
            display_data['exercise_minutes'] = display_data['exercise_minutes'].apply(lambda x: f"{x:.0f} min" if pd.notna(x) and x > 0 else "")
        
        # Select columns to display
        columns_to_show = ['date', 'weight', 'heart_rate', 'sleep_hours', 'exercise_minutes', 'mood']
        available_columns = [col for col in columns_to_show if col in display_data.columns]
        
        if available_columns:
            st.dataframe(
                display_data[available_columns],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No recent entries found. Start by adding your first health entry above!")
    
    # Health tips
    st.header("💡 Health Tips")
    
    tips = [
        "📱 Track consistently - daily logging helps identify patterns",
        "🎯 Set realistic goals - small improvements lead to big changes",
        "📊 Review your data weekly to spot trends",
        "🤖 Use AI insights to get personalized recommendations",
        "👥 Share your progress with healthcare providers"
    ]
    
    for tip in tips:
        st.info(tip)
