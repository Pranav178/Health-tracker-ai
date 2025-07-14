import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from visualizations import HealthVisualizations
from utils import get_health_score, create_metric_card, format_health_tip

def show_dashboard():
    """Display the main dashboard with health metrics and visualizations"""
    st.title("📊 Health Dashboard")
    st.markdown("Welcome to your personal health tracking dashboard!")
    
    # Get database manager from session state
    database_manager = st.session_state.database_manager
    
    # Get health data
    health_data = database_manager.get_health_data(30)  # Last 30 days
    latest_entry = database_manager.get_latest_entry()
    health_summary = database_manager.get_health_summary()
    
    # Create visualizations instance
    viz = HealthVisualizations()
    
    # Display overview metrics
    st.header("📈 Health Overview")
    
    if health_data.empty:
        st.info("👋 Welcome! Start by adding your health data in the **Data Entry** section to see your personalized dashboard.")
        st.markdown("### Getting Started")
        st.markdown("""
        1. **📝 Log your data**: Go to the Data Entry page to record your health metrics
        2. **📊 Track progress**: View your trends and patterns here on the dashboard
        3. **🤖 Get insights**: Visit the AI Insights page for personalized recommendations
        4. **🎯 Set goals**: Create and track health goals in the Goals section
        """)
        return
    
    # Health score and metrics
    health_score, score_factors = get_health_score(health_data)
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Health Score",
            f"{health_score}/100",
            help="Overall health score based on recent data"
        )
    
    with col2:
        st.metric(
            "Data Points",
            health_summary.get('total_entries', 0),
            help="Total number of health entries logged"
        )
    
    with col3:
        if health_summary.get('avg_weight', 0) > 0:
            st.metric(
                "Avg Weight",
                f"{health_summary.get('avg_weight', 0):.1f} kg",
                help="Average weight over the last 30 days"
            )
        else:
            st.metric("Avg Weight", "No data", help="No weight data available")
    
    with col4:
        if health_summary.get('avg_sleep', 0) > 0:
            st.metric(
                "Avg Sleep",
                f"{health_summary.get('avg_sleep', 0):.1f} hrs",
                help="Average sleep hours over the last 30 days"
            )
        else:
            st.metric("Avg Sleep", "No data", help="No sleep data available")
    
    # Health score details
    if score_factors:
        st.success(f"🎉 **Health Score Factors**: {', '.join(score_factors)}")
    
    # Latest entry information
    if latest_entry:
        st.markdown("### 📅 Latest Entry")
        entry_date = latest_entry.get('date', 'Unknown')
        st.info(f"**Last updated**: {entry_date}")
        
        # Show latest values in columns
        latest_cols = st.columns(3)
        
        with latest_cols[0]:
            if latest_entry.get('weight') and pd.notna(latest_entry['weight']):
                st.metric("Weight", f"{latest_entry['weight']:.1f} kg")
            if latest_entry.get('heart_rate') and pd.notna(latest_entry['heart_rate']):
                st.metric("Heart Rate", f"{latest_entry['heart_rate']:.0f} bpm")
        
        with latest_cols[1]:
            if (latest_entry.get('blood_pressure_systolic') and 
                latest_entry.get('blood_pressure_diastolic') and
                pd.notna(latest_entry['blood_pressure_systolic']) and
                pd.notna(latest_entry['blood_pressure_diastolic'])):
                st.metric("Blood Pressure", 
                         f"{latest_entry['blood_pressure_systolic']:.0f}/{latest_entry['blood_pressure_diastolic']:.0f}")
            if latest_entry.get('sleep_hours') and pd.notna(latest_entry['sleep_hours']):
                st.metric("Sleep", f"{latest_entry['sleep_hours']:.1f} hrs")
        
        with latest_cols[2]:
            if latest_entry.get('exercise_minutes') and pd.notna(latest_entry['exercise_minutes']):
                st.metric("Exercise", f"{latest_entry['exercise_minutes']:.0f} min")
            if latest_entry.get('mood') and pd.notna(latest_entry['mood']):
                mood_emoji = {"Excellent": "😊", "Good": "🙂", "Average": "😐", "Poor": "😔", "Very Poor": "😢"}
                st.metric("Mood", f"{mood_emoji.get(latest_entry['mood'], '😐')} {latest_entry['mood']}")
    
    # Visualizations
    st.header("📊 Health Trends")
    
    # Chart selection tabs
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["🏃‍♂️ Physical Health", "❤️ Vitals", "😊 Wellness"])
    
    with chart_tab1:
        # Weight and exercise charts
        col1, col2 = st.columns(2)
        
        with col1:
            weight_chart = viz.create_weight_trend_chart(health_data)
            if weight_chart:
                st.plotly_chart(weight_chart, use_container_width=True)
        
        with col2:
            sleep_exercise_chart = viz.create_sleep_exercise_chart(health_data)
            if sleep_exercise_chart:
                st.plotly_chart(sleep_exercise_chart, use_container_width=True)
    
    with chart_tab2:
        # Vitals charts
        col1, col2 = st.columns(2)
        
        with col1:
            bp_chart = viz.create_blood_pressure_chart(health_data)
            if bp_chart:
                st.plotly_chart(bp_chart, use_container_width=True)
        
        with col2:
            hr_chart = viz.create_heart_rate_chart(health_data)
            if hr_chart:
                st.plotly_chart(hr_chart, use_container_width=True)
    
    with chart_tab3:
        # Wellness charts
        mood_chart = viz.create_mood_chart(health_data)
        if mood_chart:
            st.plotly_chart(mood_chart, use_container_width=True)
        
        # Health metrics summary
        metrics_summary = viz.create_health_metrics_summary(health_data)
        if metrics_summary:
            st.plotly_chart(metrics_summary, use_container_width=True)
    
    # Goals progress
    st.header("🎯 Goals Progress")
    goals_data = database_manager.get_goals()
    
    if not goals_data.empty:
        active_goals = goals_data[goals_data['status'] == 'active']
        
        if not active_goals.empty:
            goal_progress_chart = viz.create_goal_progress_chart(active_goals)
            if goal_progress_chart:
                st.plotly_chart(goal_progress_chart, use_container_width=True)
            
            # Show goal details
            st.subheader("📋 Active Goals Summary")
            for _, goal in active_goals.iterrows():
                progress = (goal['current_value'] / goal['target_value']) * 100 if goal['target_value'] > 0 else 0
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{goal['description']}**")
                
                with col2:
                    st.metric("Progress", f"{progress:.1f}%")
                
                with col3:
                    days_left = (pd.to_datetime(goal['target_date']) - datetime.now()).days
                    st.metric("Days Left", f"{days_left}")
        else:
            st.info("No active goals found. Create some goals to track your progress!")
    else:
        st.info("No goals set yet. Visit the Goals page to create your first health goal!")
    
    # Health tips
    st.header("💡 Health Tips")
    
    # Generate contextual tips based on latest data
    tips = []
    if latest_entry:
        if latest_entry.get('exercise_minutes', 0) < 30:
            tips.append("🏃‍♂️ Try to get at least 30 minutes of exercise daily for better health.")
        
        if latest_entry.get('sleep_hours', 0) < 7:
            tips.append("😴 Aim for 7-9 hours of sleep per night for optimal recovery.")
        
        if latest_entry.get('mood') in ['Poor', 'Very Poor']:
            tips.append("🧘‍♂️ Consider stress management techniques like meditation or deep breathing.")
        
        if (latest_entry.get('blood_pressure_systolic', 0) > 130 or 
            latest_entry.get('blood_pressure_diastolic', 0) > 80):
            tips.append("🩺 Monitor your blood pressure regularly and consult a healthcare provider if elevated.")
    
    if not tips:
        tips = [
            "💧 Stay hydrated - aim for 8 glasses of water daily",
            "🥗 Include more fruits and vegetables in your diet",
            "🚶‍♂️ Take regular breaks to move throughout the day",
            "📱 Limit screen time before bed for better sleep quality"
        ]
    
    for tip in tips[:3]:  # Show max 3 tips
        st.info(tip)
    
    # Recent activity
    st.header("📅 Recent Activity")
    
    if not health_data.empty:
        recent_data = health_data.head(7)  # Last 7 entries
        
        st.subheader("Last 7 Health Entries")
        
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
    
    # Quick actions
    st.header("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Add Today's Data", use_container_width=True):
            st.switch_page("pages/data_entry.py")
    
    with col2:
        if st.button("🎯 Create New Goal", use_container_width=True):
            st.switch_page("pages/goals.py")
    
    with col3:
        if st.button("🤖 Get AI Insights", use_container_width=True):
            st.switch_page("pages/insights.py")
