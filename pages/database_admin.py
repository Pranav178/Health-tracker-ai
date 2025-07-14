"""Database administration page for Health Tracker AI."""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from database_manager import DatabaseManager
from utils import show_success_message, show_error_message, show_info_box
import plotly.express as px

def show_database_admin():
    """Display database administration page."""
    st.title("🗄️ Database Administration")
    st.markdown("Manage your database, view statistics, and perform maintenance tasks.")
    
    # Get database manager from session state
    database_manager = st.session_state.database_manager
    
    # Database connection status
    st.header("📊 Database Status")
    
    try:
        # Test database connection
        health_data = database_manager.get_health_data(1)
        goals_data = database_manager.get_goals()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Connection Status", "✅ Connected")
        
        with col2:
            st.metric("Health Records", len(health_data))
        
        with col3:
            st.metric("Goals", len(goals_data))
        
        # Database info
        db_url = os.getenv('DATABASE_URL', 'Not set')
        db_host = os.getenv('PGHOST', 'Not set')
        db_name = os.getenv('PGDATABASE', 'Not set')
        
        with st.expander("Database Connection Details"):
            st.markdown(f"**Host**: {db_host}")
            st.markdown(f"**Database**: {db_name}")
            st.markdown(f"**Connection String**: {db_url[:50]}...")
        
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        return
    
    # Database statistics
    st.header("📈 Database Statistics")
    
    try:
        # Get all health data
        all_health_data = database_manager.get_health_data(365)  # Last year
        all_goals = database_manager.get_goals()
        
        if not all_health_data.empty:
            # Health data statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Health Data Overview")
                st.metric("Total Records", len(all_health_data))
                st.metric("Date Range", f"{all_health_data['date'].min()} to {all_health_data['date'].max()}")
                
                # Data completeness
                completeness = {}
                for col in ['weight', 'heart_rate', 'blood_pressure_systolic', 'sleep_hours', 'exercise_minutes']:
                    if col in all_health_data.columns:
                        completeness[col] = (all_health_data[col].notna().sum() / len(all_health_data)) * 100
                
                st.subheader("Data Completeness")
                for metric, percentage in completeness.items():
                    st.metric(f"{metric.replace('_', ' ').title()}", f"{percentage:.1f}%")
            
            with col2:
                st.subheader("Goals Overview")
                if not all_goals.empty:
                    active_goals = all_goals[all_goals['status'] == 'active']
                    completed_goals = all_goals[all_goals['status'] == 'completed']
                    
                    st.metric("Active Goals", len(active_goals))
                    st.metric("Completed Goals", len(completed_goals))
                    
                    # Goal types distribution
                    goal_types = all_goals['goal_type'].value_counts()
                    fig = px.pie(values=goal_types.values, names=goal_types.index, 
                               title="Goal Types Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No goals found")
        
        # Data quality metrics
        st.header("🔍 Data Quality")
        
        if not all_health_data.empty:
            quality_issues = []
            
            # Check for missing dates
            date_gaps = []
            if len(all_health_data) > 1:
                dates = pd.to_datetime(all_health_data['date']).sort_values()
                for i in range(1, len(dates)):
                    gap = (dates.iloc[i] - dates.iloc[i-1]).days
                    if gap > 7:  # Gap longer than a week
                        date_gaps.append(f"Gap of {gap} days between {dates.iloc[i-1].strftime('%Y-%m-%d')} and {dates.iloc[i].strftime('%Y-%m-%d')}")
            
            # Check for outliers
            outliers = []
            if 'weight' in all_health_data.columns:
                weight_data = all_health_data['weight'].dropna()
                if len(weight_data) > 0:
                    q1 = weight_data.quantile(0.25)
                    q3 = weight_data.quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    weight_outliers = weight_data[(weight_data < lower_bound) | (weight_data > upper_bound)]
                    if len(weight_outliers) > 0:
                        outliers.append(f"Weight outliers: {len(weight_outliers)} records")
            
            # Display quality issues
            if date_gaps or outliers:
                st.warning("⚠️ Data Quality Issues Found:")
                for gap in date_gaps[:5]:  # Show first 5 gaps
                    st.markdown(f"• {gap}")
                for outlier in outliers:
                    st.markdown(f"• {outlier}")
            else:
                st.success("✅ No major data quality issues detected")
    
    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")
    
    # Database maintenance
    st.header("🔧 Database Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Backup & Export")
        
        if st.button("📥 Export Health Data to CSV"):
            try:
                health_data = database_manager.get_health_data(365)
                if not health_data.empty:
                    csv = health_data.to_csv(index=False)
                    st.download_button(
                        label="Download Health Data CSV",
                        data=csv,
                        file_name=f"health_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No health data to export")
            except Exception as e:
                show_error_message(f"Export failed: {str(e)}")
        
        if st.button("📥 Export Goals to CSV"):
            try:
                goals_data = database_manager.get_goals()
                if not goals_data.empty:
                    csv = goals_data.to_csv(index=False)
                    st.download_button(
                        label="Download Goals CSV",
                        data=csv,
                        file_name=f"goals_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No goals to export")
            except Exception as e:
                show_error_message(f"Export failed: {str(e)}")
        
        if st.button("💾 Create Database Backup"):
            try:
                if database_manager.backup_database_to_csv():
                    show_success_message("Database backup created successfully!")
                else:
                    show_error_message("Backup failed")
            except Exception as e:
                show_error_message(f"Backup failed: {str(e)}")
    
    with col2:
        st.subheader("Data Migration")
        
        if st.button("📊 Migrate CSV to Database"):
            try:
                if database_manager.migrate_csv_to_database():
                    show_success_message("CSV data migrated successfully!")
                    st.rerun()
                else:
                    show_error_message("Migration failed")
            except Exception as e:
                show_error_message(f"Migration failed: {str(e)}")
        
        st.subheader("Database Initialization")
        
        if st.button("🔄 Initialize Database Tables"):
            try:
                from database_models import init_database
                if init_database():
                    show_success_message("Database tables initialized successfully!")
                else:
                    show_error_message("Database initialization failed")
            except Exception as e:
                show_error_message(f"Initialization failed: {str(e)}")
    
    # Data viewer
    st.header("📋 Data Viewer")
    
    tab1, tab2 = st.tabs(["Health Data", "Goals Data"])
    
    with tab1:
        st.subheader("Recent Health Data")
        
        # Date range selector
        col1, col2 = st.columns(2)
        
        with col1:
            days_to_show = st.selectbox("Show last:", [7, 30, 90, 365], index=1)
        
        with col2:
            if st.button("🔄 Refresh Health Data"):
                st.rerun()
        
        try:
            health_data = database_manager.get_health_data(days_to_show)
            
            if not health_data.empty:
                # Show summary
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Records", len(health_data))
                
                with col2:
                    if 'weight' in health_data.columns:
                        avg_weight = health_data['weight'].mean()
                        st.metric("Avg Weight", f"{avg_weight:.1f} kg" if not pd.isna(avg_weight) else "N/A")
                
                with col3:
                    if 'exercise_minutes' in health_data.columns:
                        total_exercise = health_data['exercise_minutes'].sum()
                        st.metric("Total Exercise", f"{total_exercise:.0f} min" if not pd.isna(total_exercise) else "N/A")
                
                # Data table
                st.dataframe(
                    health_data.fillna('-'),
                    use_container_width=True,
                    column_config={
                        'date': 'Date',
                        'weight': 'Weight (kg)',
                        'blood_pressure_systolic': 'BP Systolic',
                        'blood_pressure_diastolic': 'BP Diastolic',
                        'heart_rate': 'Heart Rate',
                        'sleep_hours': 'Sleep (hrs)',
                        'exercise_minutes': 'Exercise (min)',
                        'mood': 'Mood'
                    }
                )
            else:
                st.info("No health data found for the selected period")
        
        except Exception as e:
            st.error(f"Error loading health data: {str(e)}")
    
    with tab2:
        st.subheader("Goals Data")
        
        if st.button("🔄 Refresh Goals"):
            st.rerun()
        
        try:
            goals_data = database_manager.get_goals()
            
            if not goals_data.empty:
                # Goals summary
                active_goals = goals_data[goals_data['status'] == 'active']
                completed_goals = goals_data[goals_data['status'] == 'completed']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Goals", len(goals_data))
                
                with col2:
                    st.metric("Active Goals", len(active_goals))
                
                with col3:
                    st.metric("Completed Goals", len(completed_goals))
                
                # Goals table
                st.dataframe(
                    goals_data,
                    use_container_width=True,
                    column_config={
                        'goal_id': 'ID',
                        'goal_type': 'Type',
                        'target_value': 'Target',
                        'current_value': 'Current',
                        'target_date': 'Target Date',
                        'created_date': 'Created',
                        'status': 'Status',
                        'description': 'Description'
                    }
                )
            else:
                st.info("No goals found")
        
        except Exception as e:
            st.error(f"Error loading goals data: {str(e)}")
    
    # System information
    st.header("ℹ️ System Information")
    
    with st.expander("Environment Variables"):
        env_vars = ['DATABASE_URL', 'PGHOST', 'PGPORT', 'PGUSER', 'PGDATABASE', 'OPENAI_API_KEY']
        
        for var in env_vars:
            value = os.getenv(var, 'Not set')
            if var in ['DATABASE_URL', 'OPENAI_API_KEY']:
                # Hide sensitive values
                display_value = value[:10] + '...' if value != 'Not set' else value
            else:
                display_value = value
            
            st.markdown(f"**{var}**: {display_value}")
