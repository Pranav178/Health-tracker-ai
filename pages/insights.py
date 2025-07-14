import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils import show_info_box, show_error_message, get_health_score

def show_insights():
    """Display AI-powered health insights and recommendations"""
    st.title("🤖 AI Health Insights")
    st.markdown("Get personalized health recommendations and insights powered by AI.")
    
    # Get database manager and AI insights from session state
    database_manager = st.session_state.database_manager
    ai_insights = st.session_state.ai_insights
    
    # Get health data
    health_data = database_manager.get_health_data(30)  # Last 30 days
    
    if health_data.empty:
        st.warning("⚠️ No health data available for analysis.")
        st.info("""
        🔍 **To get personalized insights:**
        1. Log your health data in the **Data Entry** section
        2. Add at least a few days of data for better analysis
        3. Return here to see AI-powered recommendations
        """)
        return
    
    # Check if OpenAI API key is configured
    if not st.session_state.ai_insights.openai_client.api_key or st.session_state.ai_insights.openai_client.api_key == "your-openai-api-key-here":
        st.error("❌ OpenAI API key not configured. Please set your OPENAI_API_KEY environment variable.")
        st.info("💡 Add your OpenAI API key to get AI-powered health insights and recommendations.")
        return
    
    # Display current health score
    health_score, score_factors = get_health_score(health_data)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Health Score", f"{health_score}/100")
    
    with col2:
        st.metric("Data Points", len(health_data))
    
    with col3:
        st.metric("Days Tracked", len(health_data['date'].unique()))
    
    # Generate insights button
    if st.button("🔍 Generate AI Insights", use_container_width=True):
        with st.spinner("🤖 Analyzing your health data..."):
            insights = ai_insights.generate_health_insights(health_data)
            
            if insights:
                st.session_state.health_insights = insights
                st.success("✅ AI insights generated successfully!")
            else:
                show_error_message("Failed to generate insights. Please try again.")
    
    # Display insights if available
    if hasattr(st.session_state, 'health_insights') and st.session_state.health_insights:
        insights = st.session_state.health_insights
        
        # Overall health assessment
        st.header("🏥 Overall Health Assessment")
        show_info_box("AI Health Analysis", insights.get('overall_health', 'No assessment available'))
        
        # Recommendations
        st.header("💡 Personalized Recommendations")
        recommendations = insights.get('recommendations', [])
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"**{i}.** {rec}")
        else:
            st.info("No specific recommendations available.")
        
        # Trends analysis
        st.header("📈 Health Trends")
        trends = insights.get('trends', [])
        
        if trends:
            for trend in trends:
                st.markdown(f"• {trend}")
        else:
            st.info("No significant trends identified.")
        
        # Risk factors
        st.header("⚠️ Risk Factors")
        risk_factors = insights.get('risk_factors', [])
        
        if risk_factors:
            for risk in risk_factors:
                st.warning(f"⚠️ {risk}")
        else:
            st.success("🎉 No significant risk factors identified!")
        
        # Positive aspects
        if 'positive_aspects' in insights:
            st.header("✅ Positive Health Indicators")
            positive_aspects = insights.get('positive_aspects', [])
            
            if positive_aspects:
                for aspect in positive_aspects:
                    st.success(f"✅ {aspect}")
        
        # Areas for improvement
        if 'areas_for_improvement' in insights:
            st.header("🎯 Areas for Improvement")
            improvements = insights.get('areas_for_improvement', [])
            
            if improvements:
                for improvement in improvements:
                    st.info(f"🎯 {improvement}")
    
    # Trend analysis section
    st.header("📊 Trend Analysis")
    
    if st.button("📈 Analyze Health Trends", use_container_width=True):
        with st.spinner("📊 Analyzing trends and patterns..."):
            trend_analysis = ai_insights.analyze_health_trends(health_data)
            
            if trend_analysis:
                st.session_state.trend_analysis = trend_analysis
                st.success("✅ Trend analysis completed!")
            else:
                show_error_message("Failed to analyze trends. Please try again.")
    
    # Display trend analysis if available
    if hasattr(st.session_state, 'trend_analysis') and st.session_state.trend_analysis:
        trend_analysis = st.session_state.trend_analysis
        
        st.subheader("📈 Trend Insights")
        
        # Statistical insights
        if 'statistical_insights' in trend_analysis:
            st.markdown("**Statistical Analysis:**")
            for insight in trend_analysis['statistical_insights']:
                st.markdown(f"• {insight}")
        
        # Correlations
        if 'correlations' in trend_analysis:
            st.markdown("**Correlations Found:**")
            for correlation in trend_analysis['correlations']:
                st.markdown(f"• {correlation}")
        
        # Patterns
        if 'patterns' in trend_analysis:
            st.markdown("**Patterns Identified:**")
            for pattern in trend_analysis['patterns']:
                st.markdown(f"• {pattern}")
    
    # Goal recommendations section
    st.header("🎯 AI Goal Recommendations")
    
    if st.button("🤖 Generate Goal Suggestions", use_container_width=True):
        with st.spinner("🎯 Generating personalized goal recommendations..."):
            # Get existing goals
            existing_goals = database_manager.get_goals()
            
            goal_recommendations = ai_insights.generate_goal_recommendations(health_data, existing_goals)
            
            if goal_recommendations:
                st.session_state.goal_recommendations = goal_recommendations
                st.success("✅ Goal recommendations generated!")
            else:
                show_error_message("Failed to generate goal recommendations. Please try again.")
    
    # Display goal recommendations if available
    if hasattr(st.session_state, 'goal_recommendations') and st.session_state.goal_recommendations:
        recommendations = st.session_state.goal_recommendations
        
        st.subheader("🎯 Recommended Goals")
        
        if 'recommended_goals' in recommendations:
            for i, goal in enumerate(recommendations['recommended_goals'], 1):
                with st.container():
                    st.markdown(f"**Goal {i}:** {goal}")
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col2:
                        if st.button(f"Create Goal {i}", key=f"create_goal_{i}"):
                            st.info("Redirect to Goals page to create this goal!")
                    
                    st.divider()
        
        # Rationale
        if 'rationale' in recommendations:
            st.subheader("💭 Why These Goals?")
            st.markdown(recommendations['rationale'])
    
    # Interactive data exploration
    st.header("🔍 Interactive Data Exploration")
    
    if not health_data.empty:
        # Metric selection
        available_metrics = []
        if 'weight' in health_data.columns and health_data['weight'].notna().any():
            available_metrics.append('weight')
        if 'heart_rate' in health_data.columns and health_data['heart_rate'].notna().any():
            available_metrics.append('heart_rate')
        if 'sleep_hours' in health_data.columns and health_data['sleep_hours'].notna().any():
            available_metrics.append('sleep_hours')
        if 'exercise_minutes' in health_data.columns and health_data['exercise_minutes'].notna().any():
            available_metrics.append('exercise_minutes')
        
        if available_metrics:
            selected_metrics = st.multiselect(
                "Select metrics to explore:",
                available_metrics,
                default=available_metrics[:2] if len(available_metrics) >= 2 else available_metrics,
                help="Choose which health metrics to analyze"
            )
            
            if selected_metrics:
                # Create interactive chart
                fig = go.Figure()
                
                for metric in selected_metrics:
                    metric_data = health_data[health_data[metric].notna()]
                    
                    fig.add_trace(go.Scatter(
                        x=metric_data['date'],
                        y=metric_data[metric],
                        mode='lines+markers',
                        name=metric.replace('_', ' ').title(),
                        line=dict(width=2),
                        marker=dict(size=6)
                    ))
                
                fig.update_layout(
                    title="Health Metrics Over Time",
                    xaxis_title="Date",
                    yaxis_title="Value",
                    hovermode='x unified',
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Basic statistics
                st.subheader("📊 Basic Statistics")
                
                stats_data = {}
                for metric in selected_metrics:
                    metric_values = health_data[metric].dropna()
                    if len(metric_values) > 0:
                        stats_data[metric] = {
                            'Average': metric_values.mean(),
                            'Min': metric_values.min(),
                            'Max': metric_values.max(),
                            'Latest': metric_values.iloc[-1] if len(metric_values) > 0 else None
                        }
                
                if stats_data:
                    stats_df = pd.DataFrame(stats_data).round(2)
                    st.dataframe(stats_df, use_container_width=True)
        else:
            st.info("No numeric health metrics available for exploration.")
    
    # Health insights history
    st.header("📚 Insights History")
    
    # Get stored insights from database
    stored_insights = database_manager.get_health_insights(30)
    
    if not stored_insights.empty:
        st.subheader("Recent AI Insights")
        
        for _, insight in stored_insights.iterrows():
            with st.expander(f"{insight['insight_type'].title()} - {insight['date_generated']}"):
                st.markdown(insight['content'])
                
                if insight['confidence_score']:
                    st.caption(f"Confidence: {insight['confidence_score']:.1%}")
    else:
        st.info("No previous insights found. Generate some insights to build your history!")
    
    # Export insights
    st.header("📤 Export Insights")
    
    if st.button("📋 Export Current Insights", use_container_width=True):
        if hasattr(st.session_state, 'health_insights') and st.session_state.health_insights:
            insights_text = f"""
# Health Insights Report - {datetime.now().strftime('%Y-%m-%d')}

## Overall Health Assessment
{st.session_state.health_insights.get('overall_health', 'No assessment available')}

## Recommendations
{chr(10).join([f"• {rec}" for rec in st.session_state.health_insights.get('recommendations', [])])}

## Health
