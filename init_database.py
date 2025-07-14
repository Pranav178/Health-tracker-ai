#!/usr/bin/env python3
"""
Database initialization script for Health Tracker AI.
This script sets up the database tables and optionally migrates existing CSV data.
"""

import os
import sys
import streamlit as st
from database_models import init_database, create_tables
from database_manager import DatabaseManager

def main():
    """Main function to initialize the database."""
    st.set_page_config(
        page_title="Database Initialization",
        page_icon="🗄️",
        layout="wide"
    )
    
    st.title("🗄️ Database Initialization")
    st.write("This script initializes the Health Tracker AI database with required tables.")
    
    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        st.error("❌ DATABASE_URL environment variable is not set!")
        st.info("Please set the DATABASE_URL environment variable before running this script.")
        return
    
    st.success("✅ DATABASE_URL found")
    
    # Initialize database
    st.subheader("🔧 Initializing Database Tables")
    
    try:
        # Create database tables
        if init_database():
            st.success("✅ Database tables created successfully!")
            
            # Display table information
            st.subheader("📊 Database Tables Created")
            st.markdown("""
            The following tables have been created in your database:
            
            1. **health_data** - Stores daily health metrics
            2. **goals** - Stores user health goals and progress
            3. **users** - Stores user information (for future use)
            4. **health_insights** - Stores AI-generated health insights
            """)
            
            # Optional: Migrate existing CSV data
            st.subheader("📁 CSV Data Migration (Optional)")
            st.info("If you have existing CSV data files, you can migrate them to the database.")
            
            if st.button("Migrate CSV Data"):
                try:
                    db_manager = DatabaseManager()
                    if db_manager.migrate_csv_to_database():
                        st.success("✅ CSV data migrated successfully!")
                    else:
                        st.warning("⚠️ No CSV data found or migration failed.")
                except Exception as e:
                    st.error(f"❌ Error during CSV migration: {str(e)}")
            
            # Database connection test
            st.subheader("🔍 Database Connection Test")
            if st.button("Test Database Connection"):
                try:
                    db_manager = DatabaseManager()
                    health_data = db_manager.get_health_data(days=1)
                    st.success("✅ Database connection successful!")
                    st.info(f"Found {len(health_data)} health records in the database.")
                except Exception as e:
                    st.error(f"❌ Database connection failed: {str(e)}")
            
        else:
            st.error("❌ Failed to create database tables!")
            
    except Exception as e:
        st.error(f"❌ Database initialization failed: {str(e)}")
        st.info("Please check your DATABASE_URL and database permissions.")

if __name__ == "__main__":
    main()
