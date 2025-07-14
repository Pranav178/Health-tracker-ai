import json
import os
import streamlit as st
from openai import OpenAI
import pandas as pd
from datetime import datetime, timedelta

class AIInsights:
    """Handles AI-powered health insights and recommendations"""
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
        )
        self.model = "gpt-4o"
    
    def generate_health_insights(self, health_data):
        """Generate AI-powered health insights from user data"""
        try:
            if health_data.empty:
                return {
                    "overall_health": "No data available for analysis",
                    "recommendations": ["Please log your health data to receive personalized insights"],
                    "trends": [],
                    "risk_factors": []
                }
            
            # Prepare data summary for AI analysis
            data_summary = self._prepare_data_summary(health_data)
            
            prompt = f"""
            You are a health analysis AI assistant. Based on the following health data summary, 
            provide comprehensive health insights and recommendations.
            
            Health Data Summary:
            {data_summary}
            
            Please provide a detailed analysis in JSON format with the following structure:
            {{
                "overall_health": "Brief overall health assessment",
                "recommendations": ["List of 3-5 specific actionable recommendations"],
                "trends": ["List of notable trends observed in the data"],
                "risk_factors": ["List of potential risk factors identified"],
                "positive_aspects": ["List of positive health indicators"],
                "areas_for_improvement": ["Specific areas that need attention"]
            }}
            
            Focus on:
            - Practical, actionable advice
            - Patterns and trends in the data
            - Maintaining a supportive and encouraging tone
            - Health education and awareness
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a knowledgeable health advisor AI. Provide helpful, accurate health insights while emphasizing the importance of consulting healthcare professionals for medical advice."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            insights = json.loads(response.choices[0].message.content)
            return insights
            
        except Exception as e:
            st.error(f"Error generating health insights: {str(e)}")
            return {
                "overall_health": "Unable to generate insights at this time",
                "recommendations": ["Please ensure your OpenAI API key is configured correctly"],
                "trends": [],
                "risk_factors": []
            }
    
    def generate_goal_recommendations(self, current_health_data, existing_goals):
        """Generate AI-powered goal recommendations"""
        try:
            # Prepare context for AI
            health_context = self._prepare_data_summary(current_health_data)
            goals_context = self._prepare_goals_summary(existing_goals)
            
            prompt = f"""
            Based on the user's health data and existing goals, recommend 3-5 SMART health goals.
            
            Current Health Data:
            {health_context}
            
            Existing Goals:
            {goals_context}
            
            Please provide goal recommendations in JSON format:
            {{
                "recommended_goals": [
                    {{
                        "goal_type": "weight_loss|exercise|sleep|heart_health|nutrition",
                        "description": "Clear, specific goal description",
                        "target_value": "numeric target value",
                        "timeframe": "suggested timeframe in days",
                        "rationale": "why this goal is recommended"
                    }}
                ]
            }}
            
            Ensure goals are:
            - Specific and measurable
            - Realistic and achievable
            - Time-bound
            - Based on current health data
            - Not duplicating existing active goals
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a health goal advisor. Recommend SMART health goals based on user data."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            recommendations = json.loads(response.choices[0].message.content)
            return recommendations.get("recommended_goals", [])
            
        except Exception as e:
            st.error(f"Error generating goal recommendations: {str(e)}")
            return []
    
    def analyze_health_trends(self, health_data):
        """Analyze health trends and patterns"""
        try:
            if health_data.empty:
                return {"trends": [], "patterns": []}
            
            # Prepare trend data
            trend_data = self._prepare_trend_analysis(health_data)
            
            prompt = f"""
            Analyze the following health trend data and identify significant patterns:
            
            {trend_data}
            
            Provide analysis in JSON format:
            {{
                "trends": [
                    {{
                        "metric": "health metric name",
                        "trend": "increasing|decreasing|stable",
                        "significance": "high|medium|low",
                        "description": "detailed trend description"
                    }}
                ],
                "patterns": [
                    {{
                        "pattern": "pattern description",
                        "correlation": "related metrics or factors",
                        "recommendation": "suggested action"
                    }}
                ]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a health data analyst. Identify meaningful trends and patterns in health data."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            st.error(f"Error analyzing health trends: {str(e)}")
            return {"trends": [], "patterns": []}
    
    def _prepare_data_summary(self, health_data):
        """Prepare health data summary for AI analysis"""
        if health_data.empty:
            return "No health data available"
        
        # Calculate recent averages and trends
        recent_data = health_data.tail(7)  # Last 7 entries
        
        summary = {
            "total_entries": len(health_data),
            "date_range": f"{health_data['date'].min().strftime('%Y-%m-%d')} to {health_data['date'].max().strftime('%Y-%m-%d')}",
            "recent_averages": {}
        }
        
        # Calculate averages for numeric columns
        numeric_columns = ['weight', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                          'heart_rate', 'sleep_hours', 'exercise_minutes']
        
        for col in numeric_columns:
            if col in health_data.columns:
                recent_avg = recent_data[col].mean()
                overall_avg = health_data[col].mean()
                if not pd.isna(recent_avg) and not pd.isna(overall_avg):
                    summary["recent_averages"][col] = {
                        "recent": round(recent_avg, 2),
                        "overall": round(overall_avg, 2),
                        "trend": "improving" if recent_avg < overall_avg and col in ['weight', 'blood_pressure_systolic', 'blood_pressure_diastolic'] else "stable"
                    }
        
        # Include mood and symptoms patterns
        if 'mood' in health_data.columns:
            mood_counts = recent_data['mood'].value_counts()
            summary["recent_mood_pattern"] = mood_counts.to_dict()
        
        return json.dumps(summary, indent=2)
    
    def _prepare_goals_summary(self, goals_data):
        """Prepare goals summary for AI analysis"""
        if goals_data.empty:
            return "No existing goals"
        
        active_goals = goals_data[goals_data['status'] == 'active']
        completed_goals = goals_data[goals_data['status'] == 'completed']
        
        summary = {
            "active_goals": len(active_goals),
            "completed_goals": len(completed_goals),
            "goal_types": active_goals['goal_type'].tolist() if not active_goals.empty else [],
            "recent_goals": active_goals[['goal_type', 'target_value', 'current_value', 'description']].to_dict('records')
        }
        
        return json.dumps(summary, indent=2)
    
    def _prepare_trend_analysis(self, health_data):
        """Prepare data for trend analysis"""
        if health_data.empty:
            return "No trend data available"
        
        # Calculate week-over-week changes
        health_data = health_data.sort_values('date')
        
        trend_info = {}
        numeric_columns = ['weight', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                          'heart_rate', 'sleep_hours', 'exercise_minutes']
        
        for col in numeric_columns:
            if col in health_data.columns and not health_data[col].isna().all():
                values = health_data[col].dropna()
                if len(values) > 1:
                    # Calculate simple trend
                    first_half = values[:len(values)//2].mean()
                    second_half = values[len(values)//2:].mean()
                    change = ((second_half - first_half) / first_half) * 100 if first_half != 0 else 0
                    
                    trend_info[col] = {
                        "values": values.tolist()[-10:],  # Last 10 values
                        "change_percentage": round(change, 2),
                        "current_value": values.iloc[-1],
                        "min_value": values.min(),
                        "max_value": values.max()
                    }
        
        return json.dumps(trend_info, indent=2)
