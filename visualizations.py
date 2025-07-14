import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import numpy as np

class HealthVisualizations:
    """Handles all visualization components for the health tracking application"""
    
    def __init__(self):
        self.colors = {
            'primary': '#2E8B57',
            'secondary': '#4682B4', 
            'accent': '#FF6B6B',
            'warning': '#FFA500',
            'success': '#32CD32',
            'background': '#F0F8FF'
        }
    
    def create_weight_trend_chart(self, health_data):
        """Create weight trend line chart"""
        if health_data.empty or 'weight' not in health_data.columns:
            return self._create_empty_chart("No weight data available")
        
        weight_data = health_data.dropna(subset=['weight'])
        if weight_data.empty:
            return self._create_empty_chart("No weight data available")
        
        fig = go.Figure()
        
        # Add weight trend line
        fig.add_trace(go.Scatter(
            x=weight_data['date'],
            y=weight_data['weight'],
            mode='lines+markers',
            name='Weight',
            line=dict(color=self.colors['primary'], width=3),
            marker=dict(size=8, color=self.colors['primary'])
        ))
        
        # Add trend line
        if len(weight_data) > 1:
            z = np.polyfit(range(len(weight_data)), weight_data['weight'], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=weight_data['date'],
                y=p(range(len(weight_data))),
                mode='lines',
                name='Trend',
                line=dict(color=self.colors['accent'], dash='dash', width=2)
            ))
        
        fig.update_layout(
            title='Weight Trend Over Time',
            xaxis_title='Date',
            yaxis_title='Weight (kg)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_blood_pressure_chart(self, health_data):
        """Create blood pressure chart"""
        if health_data.empty:
            return self._create_empty_chart("No blood pressure data available")
        
        bp_data = health_data.dropna(subset=['blood_pressure_systolic', 'blood_pressure_diastolic'])
        if bp_data.empty:
            return self._create_empty_chart("No blood pressure data available")
        
        fig = go.Figure()
        
        # Systolic pressure
        fig.add_trace(go.Scatter(
            x=bp_data['date'],
            y=bp_data['blood_pressure_systolic'],
            mode='lines+markers',
            name='Systolic',
            line=dict(color=self.colors['accent'], width=3),
            marker=dict(size=8)
        ))
        
        # Diastolic pressure
        fig.add_trace(go.Scatter(
            x=bp_data['date'],
            y=bp_data['blood_pressure_diastolic'],
            mode='lines+markers',
            name='Diastolic',
            line=dict(color=self.colors['secondary'], width=3),
            marker=dict(size=8)
        ))
        
        # Add reference lines for healthy ranges
        fig.add_hline(y=120, line_dash="dash", line_color="orange", 
                     annotation_text="Systolic Target")
        fig.add_hline(y=80, line_dash="dash", line_color="blue", 
                     annotation_text="Diastolic Target")
        
        fig.update_layout(
            title='Blood Pressure Trends',
            xaxis_title='Date',
            yaxis_title='Blood Pressure (mmHg)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_heart_rate_chart(self, health_data):
        """Create heart rate chart"""
        if health_data.empty or 'heart_rate' not in health_data.columns:
            return self._create_empty_chart("No heart rate data available")
        
        hr_data = health_data.dropna(subset=['heart_rate'])
        if hr_data.empty:
            return self._create_empty_chart("No heart rate data available")
        
        fig = go.Figure()
        
        # Heart rate line
        fig.add_trace(go.Scatter(
            x=hr_data['date'],
            y=hr_data['heart_rate'],
            mode='lines+markers',
            name='Heart Rate',
            line=dict(color=self.colors['accent'], width=3),
            marker=dict(size=8, color=self.colors['accent']),
            fill='tonexty'
        ))
        
        # Add healthy range zones
        fig.add_hrect(y0=60, y1=100, fillcolor="lightgreen", opacity=0.2,
                     annotation_text="Healthy Range", annotation_position="top left")
        
        fig.update_layout(
            title='Heart Rate Over Time',
            xaxis_title='Date',
            yaxis_title='Heart Rate (bpm)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_sleep_exercise_chart(self, health_data):
        """Create combined sleep and exercise chart"""
        if health_data.empty:
            return self._create_empty_chart("No sleep/exercise data available")
        
        sleep_data = health_data.dropna(subset=['sleep_hours'])
        exercise_data = health_data.dropna(subset=['exercise_minutes'])
        
        fig = go.Figure()
        
        # Sleep hours (bar chart)
        if not sleep_data.empty:
            fig.add_trace(go.Bar(
                x=sleep_data['date'],
                y=sleep_data['sleep_hours'],
                name='Sleep Hours',
                marker_color=self.colors['primary'],
                yaxis='y',
                opacity=0.7
            ))
        
        # Exercise minutes (line chart on secondary y-axis)
        if not exercise_data.empty:
            fig.add_trace(go.Scatter(
                x=exercise_data['date'],
                y=exercise_data['exercise_minutes'],
                mode='lines+markers',
                name='Exercise Minutes',
                line=dict(color=self.colors['secondary'], width=3),
                marker=dict(size=8),
                yaxis='y2'
            ))
        
        # Add reference lines
        fig.add_hline(y=8, line_dash="dash", line_color="green", 
                     annotation_text="Sleep Target: 8 hours")
        
        fig.update_layout(
            title='Sleep and Exercise Patterns',
            xaxis_title='Date',
            yaxis=dict(title='Sleep Hours', side='left'),
            yaxis2=dict(title='Exercise Minutes', side='right', overlaying='y'),
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_mood_chart(self, health_data):
        """Create mood distribution chart"""
        if health_data.empty or 'mood' not in health_data.columns:
            return self._create_empty_chart("No mood data available")
        
        mood_data = health_data.dropna(subset=['mood'])
        if mood_data.empty:
            return self._create_empty_chart("No mood data available")
        
        # Count mood occurrences
        mood_counts = mood_data['mood'].value_counts()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=mood_counts.index,
                values=mood_counts.values,
                hole=0.4,
                textinfo='label+percent',
                marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
            )
        ])
        
        fig.update_layout(
            title='Mood Distribution',
            template='plotly_white',
            showlegend=True
        )
        
        return fig
    
    def create_goal_progress_chart(self, goals_data):
        """Create goal progress chart"""
        if goals_data.empty:
            return self._create_empty_chart("No goals data available")
        
        active_goals = goals_data[goals_data['status'] == 'active']
        if active_goals.empty:
            return self._create_empty_chart("No active goals")
        
        fig = go.Figure()
        
        for idx, goal in active_goals.iterrows():
            progress = (goal['current_value'] / goal['target_value']) * 100 if goal['target_value'] > 0 else 0
            progress = min(progress, 100)  # Cap at 100%
            
            fig.add_trace(go.Bar(
                x=[goal['description'][:30] + '...' if len(goal['description']) > 30 else goal['description']],
                y=[progress],
                name=f"Goal {goal['goal_id']}",
                marker_color=self.colors['success'] if progress >= 100 else self.colors['primary'],
                text=f"{progress:.1f}%",
                textposition='auto'
            ))
        
        fig.update_layout(
            title='Goal Progress',
            xaxis_title='Goals',
            yaxis_title='Progress (%)',
            yaxis=dict(range=[0, 100]),
            showlegend=False,
            template='plotly_white'
        )
        
        return fig
    
    def create_health_metrics_summary(self, health_data):
        """Create summary metrics visualization"""
        if health_data.empty:
            return self._create_empty_chart("No health data available")
        
        # Calculate recent averages
        recent_data = health_data.tail(7)
        
        metrics = []
        values = []
        colors = []
        
        if 'weight' in recent_data.columns and not recent_data['weight'].isna().all():
            metrics.append('Avg Weight')
            values.append(recent_data['weight'].mean())
            colors.append(self.colors['primary'])
        
        if 'heart_rate' in recent_data.columns and not recent_data['heart_rate'].isna().all():
            metrics.append('Avg Heart Rate')
            values.append(recent_data['heart_rate'].mean())
            colors.append(self.colors['accent'])
        
        if 'sleep_hours' in recent_data.columns and not recent_data['sleep_hours'].isna().all():
            metrics.append('Avg Sleep')
            values.append(recent_data['sleep_hours'].mean())
            colors.append(self.colors['secondary'])
        
        if 'exercise_minutes' in recent_data.columns and not recent_data['exercise_minutes'].isna().all():
            metrics.append('Weekly Exercise')
            values.append(recent_data['exercise_minutes'].sum())
            colors.append(self.colors['success'])
        
        if not metrics:
            return self._create_empty_chart("No metrics data available")
        
        fig = go.Figure(data=[
            go.Bar(
                x=metrics,
                y=values,
                marker_color=colors,
                text=[f"{v:.1f}" for v in values],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='Health Metrics Summary (Last 7 Days)',
            xaxis_title='Metrics',
            yaxis_title='Values',
            template='plotly_white',
            showlegend=False
        )
        
        return fig
    
    def _create_empty_chart(self, message):
        """Create empty chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            template='plotly_white',
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            height=400
        )
        
        return fig
