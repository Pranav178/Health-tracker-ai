import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Import custom modules
from database_manager import DatabaseManager
from ai_insights import AIInsights
import utils

# Configure page
st.set_page_config(
    page_title="Health Tracker AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database manager
@st.cache_resource
def get_database_manager():
    return DatabaseManager()

# Initialize AI insights
@st.cache_resource
def get_ai_insights():
    return AIInsights()

def main():
    # Initialize session state
    if 'database_manager' not in st.session_state:
        st.session_state.database_manager = get_database_manager()
    
    if 'ai_insights' not in st.session_state:
        st.session_state.ai_insights = get_ai_insights()
    
    # Sidebar navigation
    st.sidebar.title("🏥 Health Tracker AI")
    st.sidebar.markdown("---")
    
    # Navigation menu
    pages = {
        "📊 Dashboard": "dashboard",
        "📝 Data Entry": "data_entry", 
        "🤖 AI Insights": "insights",
        "🎯 Goals": "goals",
        "🗄️ Database Admin": "database_admin"
    }
    
    selected_page = st.sidebar.selectbox("Navigate to:", list(pages.keys()))
    
    # Display current page
    page_module = pages[selected_page]
    
    if page_module == "dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif page_module == "data_entry":
        from pages.data_entry import show_data_entry
        show_data_entry()
    elif page_module == "insights":
        from pages.insights import show_insights
        show_insights()
    elif page_module == "goals":
        from pages.goals import show_goals
        show_goals()
    elif page_module == "database_admin":
        from pages.database_admin import show_database_admin
        show_database_admin()
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Quick Tips")
    st.sidebar.info("""
    - Log your health data daily for better insights
    - Set realistic and achievable goals
    - Check AI recommendations regularly
    - Monitor trends over time
    """)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("Made with ❤️ using Streamlit")

if __name__ == "__main__":
    main()
