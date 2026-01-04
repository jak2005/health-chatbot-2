import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* Hide Streamlit Toolbar and Footer */
        .stDeployButton {display:none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom Button Styling */
        .stButton > button {
            background: linear-gradient(45deg, #6b4c9a 0%, #3b82f6 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            background: linear-gradient(45deg, #7c3aed 0%, #2563eb 100%);
            color: white;
            border-color: transparent;
        }

        .stButton > button:active {
            transform: translateY(0px);
        }

        /* Clean up the Main Container padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
