import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.let_it_rain import rain
import pandas as pd
from datetime import datetime
import base58
import json
import os

# File to store participants data
STORAGE_FILE = "participants_data.json"

def init_session_state():
    """Initialize session state variables"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_wallet" not in st.session_state:
        st.session_state.current_wallet = None

def get_participants():
    """Load participants data from file"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return []

def save_participant(wallet):
    """Save new participant to file"""
    try:
        participants = get_participants()
        if wallet not in [p['wallet'] for p in participants]:
            participants.append({
                'wallet': wallet,
                'joined_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'position': len(participants) + 1
            })
            with open(STORAGE_FILE, 'w') as f:
                json.dump(participants, f)
            return True
        return False
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def login_page():
    # Apply custom page design
    st.set_page_config(page_title="Rugg Dashboard 🚀", page_icon="🦄", layout="centered")
    apply_custom_styles()
    
    # Initialize session state
    init_session_state()

    if st.session_state.logged_in:
        display_launch_dashboard()
        return

    # Header Section
    colored_header(
        label="Welcome to the Rugg Dashboard 🚀",
        description="Securely log in with your Solana Wallet to get started.",
        color_name="violet-80",
    )
    
    rain(emoji="✨", falling_speed=3, animation_length="infinite")

    # Login Panel
    st.write("")
    with st.container():
        st.markdown(
            """
            <div style="background: #1f1f2e; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
                <h3 style="color: #ffffff; text-align: center; font-weight: bold;">Secure Login</h3>
                <p style="color: #d4d4e4; text-align: center;">Enter your credentials below</p>
            </div>
            """, unsafe_allow_html=True,
        )
        st.write("")

        # Display Login Form
        with st.form("login_form", clear_on_submit=True):
            wallet = st.text_input("🔑 Solana Wallet Address", placeholder="e.g., A12bC3d...XYZ", key="wallet_input")
            key = st.text_input("🔒 Solana Private Key", type="password", placeholder="Enter your private key", key="private_key_input")
            submitted = st.form_submit_button("Login 🔓")

            if submitted and validate_credentials(wallet, key):
                save_participant(wallet)
                st.session_state.logged_in = True
                st.session_state.current_wallet = wallet
                st.success("🎉 Login successful!")
                st.rerun()

    # Footer Section
    st.markdown(
        """
        <hr style="border: none; border-top: 1px solid #444;">
        <p style="text-align: center; color: #999;">
        Need help? <a href="https://discord.gg/SAyZsAG5" target="_blank" style="color: #ffffff; text-decoration: none;"><strong>Join our Discord</strong></a>
        </p>
        """,
        unsafe_allow_html=True,
    )

def display_launch_dashboard():
    st.title("Launch Dashboard 🚀")
    
    # Get current participants data
    participants = get_participants()
    
    # Dashboard Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        user_position = next((p['position'] for p in participants if p['wallet'] == st.session_state.current_wallet), "N/A")
        st.metric("Your Position", user_position)
    with col2:
        st.metric("Total Participants", len(participants))
    with col3:
        remaining = 1000 - len(participants)
        st.metric("Spots Remaining", f"{remaining}/1000")

    # Participants Table
    st.header("🎯 Secured Positions")
    if participants:
        df = pd.DataFrame(participants)
        # Highlight current user's row
        def highlight_current_user(row):
            if row['wallet'] == st.session_state.current_wallet:
                return ['background-color: #2c3e50'] * len(row)
            return [''] * len(row)
        
        styled_df = df.style.apply(highlight_current_user, axis=1)
        st.dataframe(styled_df, hide_index=True)
    
    # Launch Info
    st.header("📊 Launch Details")
    st.markdown("""
        - Initial Price: 5 SOL
        - Max Supply: 1,000
        - Whitelist Spots: 500
        - Public Sale: TBA
    """)

    # Logout Option
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_wallet = None
        st.rerun()

def validate_credentials(wallet, key):
    return validate_solana_address(wallet) and validate_solana_private_key(key)

def validate_solana_address(address):
    try:
        decoded = base58.b58decode(address)
        return len(decoded) in [32, 44]
    except ValueError:
        return False

def validate_solana_private_key(key):
    try:
        decoded = base58.b58decode(key)
        return len(decoded) == 32 or len(decoded) == 64
    except ValueError:
        return False

def apply_custom_styles():
    st.markdown(
        """
        <style>
        body {
            background-color: #121212;
            color: #d4d4e4;
            font-family: 'Arial', sans-serif;
        }

        input {
            border-radius: 10px !important;
            padding: 10px !important;
            background-color: #1f1f2e !important;
            color: #ffffff !important;
            border: 1px solid #444444 !important;
        }

        button {
            background-color: #5c6bc0 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-size: 16px !important;
            font-weight: bold !important;
            color: #ffffff !important;
            cursor: pointer !important;
            box-shadow: 0 4px 15px rgba(92, 107, 192, 0.5);
        }

        button:hover {
            background-color: #7986cb !important;
        }

        .stForm {
            border-radius: 15px !important;
            background-color: #1f1f2e !important;
            padding: 25px !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        }

        .stAlert {
            border-radius: 10px !important;
            padding: 15px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    login_page()
