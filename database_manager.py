"""Database manager for the Health Tracker AI application."""

import pandas as pd
import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc, asc
from datetime import datetime, timedelta, date
import os
from typing import Optional, List, Dict, Any
from database_models import HealthData, Goals, HealthInsights, Base, get_database_session
import json

class DatabaseManager:
    """Enhanced data manager that uses PostgreSQL database instead of CSV files."""
    
    def __init__(self):
        """Initialize the database manager."""
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.init_database()
    
    def init_database(self):
        """Initialize database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
        except Exception as e:
            st.error(f"Error initializing database: {str(e)}")
    
    def get_session(self):
        """Get database session."""
        return self.SessionLocal()
    
    def save_health_data(self, data: Dict[str, Any]) -> bool:
        """Save health data entry to database."""
        try:
            session = self.get_session()
            
            # Convert date string to date object
            entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            
            # Check if entry for this date already exists
            existing_entry = session.query(HealthData).filter(
                HealthData.date == entry_date
            ).first()
            
            if existing_entry:
                # Update existing entry
                for key, value in data.items():
                    if key != 'date' and hasattr(existing_entry, key):
                        setattr(existing_entry, key, value)
                existing_entry.updated_at = datetime.utcnow()
            else:
                # Create new entry
                health_entry = HealthData(
                    date=entry_date,
                    weight=data.get('weight'),
                    blood_pressure_systolic=data.get('blood_pressure_systolic'),
                    blood_pressure_diastolic=data.get('blood_pressure_diastolic'),
                    heart_rate=data.get('heart_rate'),
                    sleep_hours=data.get('sleep_hours'),
                    exercise_minutes=data.get('exercise_minutes'),
                    mood=data.get('mood'),
                    symptoms=data.get('symptoms'),
                    notes=data.get('notes')
                )
                session.add(health_entry)
            
            session.commit()
            session.close()
            return True
            
        except Exception as e:
            st.error(f"Error saving health data: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def get_health_data(self, days: int = 30) -> pd.DataFrame:
        """Get health data for the last n days."""
        try:
            session = self.get_session()
            
            # Calculate cutoff date
            cutoff_date = datetime.now().date() - timedelta(days=days)
            
            # Query health data
            query = session.query(HealthData).filter(
                HealthData.date >= cutoff_date
            ).order_by(asc(HealthData.date))
            
            # Convert to pandas DataFrame
            data = []
            for entry in query:
                data.append({
                    'date': entry.date,
                    'weight': entry.weight,
                    'blood_pressure_systolic': entry.blood_pressure_systolic,
                    'blood_pressure_diastolic': entry.blood_pressure_diastolic,
                    'heart_rate': entry.heart_rate,
                    'sleep_hours': entry.sleep_hours,
                    'exercise_minutes': entry.exercise_minutes,
                    'mood': entry.mood,
                    'symptoms': entry.symptoms,
                    'notes': entry.notes
                })
            
            session.close()
            return pd.DataFrame(data)
            
        except Exception as e:
            st.error(f"Error loading health data: {str(e)}")
            if session:
                session.close()
            return pd.DataFrame()
    
    def get_latest_entry(self) -> Optional[Dict[str, Any]]:
        """Get the most recent health data entry."""
        try:
            session = self.get_session()
            
            latest_entry = session.query(HealthData).order_by(
                desc(HealthData.date)
            ).first()
            
            if latest_entry:
                result = {
                    'date': latest_entry.date.strftime('%Y-%m-%d'),
                    'weight': latest_entry.weight,
                    'blood_pressure_systolic': latest_entry.blood_pressure_systolic,
                    'blood_pressure_diastolic': latest_entry.blood_pressure_diastolic,
                    'heart_rate': latest_entry.heart_rate,
                    'sleep_hours': latest_entry.sleep_hours,
                    'exercise_minutes': latest_entry.exercise_minutes,
                    'mood': latest_entry.mood,
                    'symptoms': latest_entry.symptoms,
                    'notes': latest_entry.notes
                }
                session.close()
                return result
            
            session.close()
            return None
            
        except Exception as e:
            st.error(f"Error getting latest entry: {str(e)}")
            if session:
                session.close()
            return None
    
    def save_goal(self, goal_data: Dict[str, Any]) -> bool:
        """Save a new goal to database."""
        try:
            session = self.get_session()
            
            # Convert target_date string to date object
            target_date = datetime.strptime(goal_data['target_date'], '%Y-%m-%d').date()
            
            goal = Goals(
                goal_type=goal_data['goal_type'],
                target_value=goal_data['target_value'],
                current_value=goal_data.get('current_value', 0.0),
                target_date=target_date,
                description=goal_data['description'],
                status='active'
            )
            
            session.add(goal)
            session.commit()
            session.close()
            return True
            
        except Exception as e:
            st.error(f"Error saving goal: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def get_goals(self) -> pd.DataFrame:
        """Get all goals from database."""
        try:
            session = self.get_session()
            
            goals = session.query(Goals).order_by(desc(Goals.created_at)).all()
            
            data = []
            for goal in goals:
                data.append({
                    'goal_id': goal.id,
                    'goal_type': goal.goal_type,
                    'target_value': goal.target_value,
                    'current_value': goal.current_value,
                    'target_date': goal.target_date.strftime('%Y-%m-%d'),
                    'created_date': goal.created_date.strftime('%Y-%m-%d'),
                    'status': goal.status,
                    'description': goal.description
                })
            
            session.close()
            return pd.DataFrame(data)
            
        except Exception as e:
            st.error(f"Error loading goals: {str(e)}")
            if session:
                session.close()
            return pd.DataFrame()
    
    def update_goal_progress(self, goal_id: int, current_value: float) -> bool:
        """Update goal progress in database."""
        try:
            session = self.get_session()
            
            goal = session.query(Goals).filter(Goals.id == goal_id).first()
            if goal:
                goal.current_value = current_value
                goal.updated_at = datetime.utcnow()
                
                # Check if goal is completed
                if current_value >= goal.target_value:
                    goal.status = 'completed'
                
                session.commit()
                session.close()
                return True
            
            session.close()
            return False
            
        except Exception as e:
            st.error(f"Error updating goal progress: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary statistics for health data."""
        try:
            session = self.get_session()
            
            # Get all health data
            all_data = session.query(HealthData).all()
            
            if not all_data:
                session.close()
                return {}
            
            # Calculate statistics
            weights = [entry.weight for entry in all_data if entry.weight]
            heart_rates = [entry.heart_rate for entry in all_data if entry.heart_rate]
            sleep_hours = [entry.sleep_hours for entry in all_data if entry.sleep_hours]
            exercise_minutes = [entry.exercise_minutes for entry in all_data if entry.exercise_minutes]
            
            summary = {
                'total_entries': len(all_data),
                'avg_weight': sum(weights) / len(weights) if weights else 0,
                'avg_heart_rate': sum(heart_rates) / len(heart_rates) if heart_rates else 0,
                'avg_sleep_hours': sum(sleep_hours) / len(sleep_hours) if sleep_hours else 0,
                'avg_exercise_minutes': sum(exercise_minutes) / len(exercise_minutes) if exercise_minutes else 0,
                'date_range': {
                    'start': min(entry.date for entry in all_data).strftime('%Y-%m-%d'),
                    'end': max(entry.date for entry in all_data).strftime('%Y-%m-%d')
                }
            }
            
            session.close()
            return summary
            
        except Exception as e:
            st.error(f"Error getting health summary: {str(e)}")
            if session:
                session.close()
            return {}
    
    def save_health_insight(self, insight_type: str, content: str, confidence_score: float = None) -> bool:
        """Save AI-generated health insight to database."""
        try:
            session = self.get_session()
            
            insight = HealthInsights(
                insight_type=insight_type,
                content=content,
                confidence_score=confidence_score
            )
            
            session.add(insight)
            session.commit()
            session.close()
            return True
            
        except Exception as e:
            st.error(f"Error saving health insight: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def get_health_insights(self, days: int = 30) -> pd.DataFrame:
        """Get health insights from the last n days."""
        try:
            session = self.get_session()
            
            cutoff_date = datetime.now().date() - timedelta(days=days)
            
            insights = session.query(HealthInsights).filter(
                HealthInsights.date_generated >= cutoff_date
            ).order_by(desc(HealthInsights.created_at)).all()
            
            data = []
            for insight in insights:
                data.append({
                    'insight_type': insight.insight_type,
                    'content': insight.content,
                    'confidence_score': insight.confidence_score,
                    'date_generated': insight.date_generated.strftime('%Y-%m-%d'),
                    'created_at': insight.created_at
                })
            
            session.close()
            return pd.DataFrame(data)
            
        except Exception as e:
            st.error(f"Error loading health insights: {str(e)}")
            if session:
                session.close()
            return pd.DataFrame()
    
    def migrate_csv_to_database(self, csv_data_dir: str = "data") -> bool:
        """Migrate existing CSV data to database."""
        try:
            import os
            
            # Migrate health data
            health_csv_path = os.path.join(csv_data_dir, "health_data.csv")
            if os.path.exists(health_csv_path):
                health_df = pd.read_csv(health_csv_path)
                for _, row in health_df.iterrows():
                    health_data = {
                        'date': row['date'],
                        'weight': row.get('weight'),
                        'blood_pressure_systolic': row.get('blood_pressure_systolic'),
                        'blood_pressure_diastolic': row.get('blood_pressure_diastolic'),
                        'heart_rate': row.get('heart_rate'),
                        'sleep_hours': row.get('sleep_hours'),
                        'exercise_minutes': row.get('exercise_minutes'),
                        'mood': row.get('mood'),
                        'symptoms': row.get('symptoms'),
                        'notes': row.get('notes')
                    }
                    self.save_health_data(health_data)
            
            # Migrate goals data
            goals_csv_path = os.path.join(csv_data_dir, "goals.csv")
            if os.path.exists(goals_csv_path):
                goals_df = pd.read_csv(goals_csv_path)
                for _, row in goals_df.iterrows():
                    goal_data = {
                        'goal_type': row['goal_type'],
                        'target_value': row['target_value'],
                        'current_value': row.get('current_value', 0.0),
                        'target_date': row['target_date'],
                        'description': row['description']
                    }
                    self.save_goal(goal_data)
            
            return True
            
        except Exception as e:
            st.error(f"Error migrating CSV data: {str(e)}")
            return False
    
    def backup_database_to_csv(self, backup_dir: str = "backup") -> bool:
        """Backup database data to CSV files."""
        try:
            import os
            
            # Create backup directory
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup health data
            health_data = self.get_health_data(365)  # Get last year
            if not health_data.empty:
                health_data.to_csv(os.path.join(backup_dir, "health_data_backup.csv"), index=False)
            
            # Backup goals data
            goals_data = self.get_goals()
            if not goals_data.empty:
                goals_data.to_csv(os.path.join(backup_dir, "goals_backup.csv"), index=False)
            
            return True
            
        except Exception as e:
            st.error(f"Error backing up database: {str(e)}")
            return False
