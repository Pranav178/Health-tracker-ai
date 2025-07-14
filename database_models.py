"""Database models for the Health Tracker AI application."""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/health_tracker')

# Create database engine
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class HealthData(Base):
    """Health data model for storing daily health metrics."""
    
    __tablename__ = 'health_data'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    weight = Column(Float, nullable=True)
    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    exercise_minutes = Column(Integer, nullable=True)
    mood = Column(String(50), nullable=True)
    symptoms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Goals(Base):
    """Goals model for storing user health goals."""
    
    __tablename__ = 'goals'
    
    id = Column(Integer, primary_key=True, index=True)
    goal_type = Column(String(50), nullable=False)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    target_date = Column(Date, nullable=False)
    created_date = Column(Date, default=datetime.utcnow().date)
    status = Column(String(20), default='active')  # active, completed, paused
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    """User model for storing user information (future enhancement)."""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HealthInsights(Base):
    """Model for storing AI-generated health insights."""
    
    __tablename__ = 'health_insights'
    
    id = Column(Integer, primary_key=True, index=True)
    insight_type = Column(String(50), nullable=False)  # recommendation, trend, risk_factor
    content = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    date_generated = Column(Date, default=datetime.utcnow().date)
    data_period_start = Column(Date, nullable=True)
    data_period_end = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_database_session():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


def init_database():
    """Initialize the database with tables."""
    try:
        create_tables()
        print("Database tables created successfully!")
        return True
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False


if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
