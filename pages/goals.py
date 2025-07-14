import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
from utils import show_success_message, show_error_message, show_info_box

def show_goals():
    """Display the goals management page"""
    st.title("🎯 Health Goals")
    st.markdown("Set, track, and achieve your health goals with AI-powered recommendations.")
    
    # Get database manager from session state
    database_manager = st.session_state.database_manager
    
    # Get goals data
    goals_data = database_manager.get_goals()
    
    # Goals overview
    st.header("📊 Goals Overview")
    
    if not goals_data.empty:
        total_goals = len(goals_data)
        active_goals = len(goals_data[goals_data['status'] == 'active'])
        completed_goals = len(goals_data[goals_data['status'] == 'completed'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Goals", total_goals)
        
        with col2:
            st.metric("Active Goals", active_goals)
        
        with col3:
            st.metric("Completed Goals", completed_goals)
    else:
        st.info("👋 No goals set yet. Create your first health goal below!")
    
    # Goal management tabs
    tab1, tab2, tab3 = st.tabs(["➕ Create Goal", "📋 Active Goals", "✅ Completed Goals"])
    
    with tab1:
        show_create_goal_form(database_manager)
    
    with tab2:
        show_active_goals(database_manager, goals_data)
    
    with tab3:
        show_completed_goals(goals_data)

def show_create_goal_form(database_manager):
    """Display the goal creation form"""
    st.subheader("➕ Create New Goal")
    
    with st.form("create_goal_form"):
        # Goal type selection
        goal_types = {
            "Weight Loss": "weight_loss",
            "Weight Gain": "weight_gain", 
            "Exercise Minutes": "exercise",
            "Sleep Hours": "sleep",
            "Heart Rate": "heart_rate",
            "Blood Pressure": "blood_pressure",
            "General Health": "general"
        }
        
        goal_type_display = st.selectbox(
            "Goal Type",
            list(goal_types.keys()),
            help="Select the type of health goal you want to set"
        )
        
        goal_type = goal_types[goal_type_display]
        
        # Goal description
        description = st.text_input(
            "Goal Description",
            placeholder="e.g., Lose 5kg in 3 months",
            help="Describe your goal clearly and specifically"
        )
        
        # Target value
        target_value = st.number_input(
            "Target Value",
            min_value=0.0,
            step=0.1,
            help="The target value you want to achieve"
        )
        
        # Current value
        current_value = st.number_input(
            "Current Value",
            min_value=0.0,
            step=0.1,
            help="Your current value (starting point)"
        )
        
        # Target date
        target_date = st.date_input(
            "Target Date",
            value=date.today() + timedelta(days=30),
            min_value=date.today(),
            help="When do you want to achieve this goal?"
        )
        
        # Goal-specific guidance
        if goal_type == "weight_loss":
            st.info("💡 **Weight Loss Tip**: A healthy weight loss rate is 0.5-1kg per week. Set realistic targets!")
        elif goal_type == "exercise":
            st.info("💡 **Exercise Tip**: WHO recommends at least 150 minutes of moderate exercise per week.")
        elif goal_type == "sleep":
            st.info("💡 **Sleep Tip**: Most adults need 7-9 hours of sleep per night for optimal health.")
        elif goal_type == "heart_rate":
            st.info("💡 **Heart Rate Tip**: Lower resting heart rate often indicates better cardiovascular fitness.")
        
        # Submit button
        submitted = st.form_submit_button("🎯 Create Goal", use_container_width=True)
        
        if submitted:
            # Validate inputs
            if not description.strip():
                show_error_message("Please provide a goal description.")
                return
            
            if target_value <= 0:
                show_error_message("Target value must be greater than 0.")
                return
            
            # Prepare goal data
            goal_data = {
                'goal_type': goal_type,
                'description': description.strip(),
                'target_value': target_value,
                'current_value': current_value,
                'target_date': target_date.strftime('%Y-%m-%d'),
                'status': 'active'
            }
            
            # Save goal
            try:
                success = database_manager.save_goal(goal_data)
                
                if success:
                    show_success_message("🎉 Goal created successfully!")
                    st.balloons()
                    
                    # Show goal summary
                    st.markdown("### 📊 Goal Summary")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Goal Type", goal_type_display)
                        st.metric("Target Value", f"{target_value}")
                    
                    with col2:
                        st.metric("Current Value", f"{current_value}")
                        st.metric("Target Date", target_date.strftime('%Y-%m-%d'))
                    
                    # Calculate progress
                    progress = (current_value / target_value) * 100 if target_value > 0 else 0
                    st.progress(progress / 100)
                    st.caption(f"Progress: {progress:.1f}%")
                    
                    st.rerun()
                else:
                    show_error_message("Failed to create goal. Please try again.")
                    
            except Exception as e:
                show_error_message(f"Error creating goal: {str(e)}")

def show_active_goals(database_manager, goals_data):
    """Display active goals"""
    st.subheader("📋 Active Goals")
    
    if goals_data.empty:
        st.info("No goals created yet. Create your first goal in the 'Create Goal' tab!")
        return
    
    active_goals = goals_data[goals_data['status'] == 'active']
    
    if active_goals.empty:
        st.info("No active goals. All your goals are completed! 🎉")
        return
    
    # Goal cards
    for _, goal in active_goals.iterrows():
        with st.container():
            st.markdown(f"### 🎯 {goal['description']}")
            
            # Goal details
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Type", goal['goal_type'].replace('_', ' ').title())
            
            with col2:
                st.metric("Target", f"{goal['target_value']}")
            
            with col3:
                st.metric("Current", f"{goal['current_value']}")
            
            with col4:
                days_left = (pd.to_datetime(goal['target_date']) - datetime.now()).days
                st.metric("Days Left", f"{days_left}")
            
            # Progress bar
            progress = (goal['current_value'] / goal['target_value']) * 100 if goal['target_value'] > 0 else 0
            st.progress(min(progress / 100, 1.0))
            st.caption(f"Progress: {progress:.1f}%")
            
            # Actions
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                # Update progress
                with st.popover("📊 Update Progress"):
                    new_value = st.number_input(
                        "New Current Value",
                        min_value=0.0,
                        value=float(goal['current_value']),
                        step=0.1,
                        key=f"update_{goal['id']}"
                    )
                    
                    if st.button("Update", key=f"update_btn_{goal['id']}"):
                        try:
                            success = database_manager.update_goal_progress(goal['id'], new_value)
                            if success:
                                show_success_message("Progress updated successfully!")
                                st.rerun()
                            else:
                                show_error_message("Failed to update progress.")
                        except Exception as e:
                            show_error_message(f"Error updating progress: {str(e)}")
            
            with action_col2:
                # Mark as completed
                if st.button("✅ Mark Complete", key=f"complete_{goal['id']}"):
                    try:
                        # Update goal status to completed
                        success = database_manager.update_goal_progress(goal['id'], goal['target_value'])
                        if success:
                            show_success_message("🎉 Goal completed! Congratulations!")
                            st.balloons()
                            st.rerun()
                        else:
                            show_error_message("Failed to mark goal as complete.")
                    except Exception as e:
                        show_error_message(f"Error completing goal: {str(e)}")
            
            with action_col3:
                # Extend deadline
                with st.popover("📅 Extend Deadline"):
                    new_date = st.date_input(
                        "New Target Date",
                        value=pd.to_datetime(goal['target_date']).date(),
                        min_value=date.today(),
                        key=f"extend_{goal['id']}"
                    )
                    
                    if st.button("Extend", key=f"extend_btn_{goal['id']}"):
                        st.info("Deadline extension feature coming soon!")
            
            # Goal insights
            if progress >= 100:
                st.success("🎉 Goal achieved! Consider marking it as complete.")
            elif progress >= 75:
                st.success("🔥 You're almost there! Keep up the great work!")
            elif progress >= 50:
                st.info("📈 Good progress! You're halfway to your goal.")
            elif progress >= 25:
                st.warning("⚡ You're making progress, but consider increasing your efforts.")
            else:
                st.warning("🚀 Time to get started! Focus on consistent daily actions.")
            
            st.divider()

def show_completed_goals(goals_data):
    """Display completed goals"""
    st.subheader("✅ Completed Goals")
    
    if goals_data.empty:
        st.info("No goals created yet.")
        return
    
    completed_goals = goals_data[goals_data['status'] == 'completed']
    
    if completed_goals.empty:
        st.info("No completed goals yet. Keep working on your active goals!")
        return
    
    # Completed goals list
    for _, goal in completed_goals.iterrows():
        with st.container():
            st.markdown(f"### ✅ {goal['description']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Type", goal['goal_type'].replace('_', ' ').title())
            
            with col2:
                st.metric("Target Achieved", f"{goal['target_value']}")
            
            with col3:
                completion_date = pd.to_datetime(goal['target_date']).strftime('%Y-%m-%d')
                st.metric("Completed", completion_date)
            
            st.success("🎉 Goal completed successfully!")
            st.divider()
    
    # Completion statistics
    st.subheader("📊 Achievement Statistics")
    
    if not completed_goals.empty:
        # Goal types completed
        goal_types_completed = completed_goals['goal_type'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Completed", len(completed_goals))
        
        with col2:
            most_common_type = goal_types_completed.index[0] if len(goal_types_completed) > 0 else "None"
            st.metric("Most Common Type", most_common_type.replace('_', ' ').title())
        
        # Achievement timeline
        st.subheader("🏆 Achievement Timeline")
        
        timeline_data = completed_goals.sort_values('target_date', ascending=False)
        
        for _, goal in timeline_data.iterrows():
            completion_date = pd.to_datetime(goal['target_date']).strftime('%B %d, %Y')
            st.markdown(f"**{completion_date}**: {goal['description']} ✅")
