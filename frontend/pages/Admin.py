import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configure page settings - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="🛡️",
    layout="wide"
)

import os
import sys
# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
utils.load_css()

# Constants
API_URL = "http://127.0.0.1:5000"
ADMIN_PASSWORD = "admin"

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == ADMIN_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Enter Admin Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Enter Admin Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

def fetch_feedback():
    try:
        response = requests.get(f"{API_URL}/admin/feedback")
        if response.status_code == 200:
            return response.json().get("feedback", [])
        return []
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return []

def main():
    st.title("🛡️ Admin Dashboard")
    
    if check_password():
        st.success("Login Successful")
        
        # Feedback Section
        st.header("📝 User Feedback")
        
        if st.button("Refresh Data"):
            st.rerun()
            
        feedback_data = fetch_feedback()
        
        if feedback_data:
            df = pd.DataFrame(feedback_data)
            
            # Format columns
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Feedback", len(df))
            with col2:
                avg_rating = df['rating'].mean() if 'rating' in df.columns else 0
                st.metric("Average Rating", f"{avg_rating:.1f}/5.0")
            
            # Display Dataframe
            st.dataframe(
                df,
                column_config={
                    "rating": st.column_config.NumberColumn(
                        "Rating",
                        help="User rating (1-5)",
                        format="%d ⭐",
                    ),
                    "timestamp": "Time",
                    "user_id": "User ID",
                    "comment": "Feedback Comment",
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No feedback data available.")

if __name__ == "__main__":
    main()
