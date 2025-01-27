import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.let_it_rain import rain
import pandas as pd
from datetime import datetime
import base58

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "participants" not in st.session_state:
    st.session_state.participants = []
if "current_wallet" not in st.session_state:
    st.session_state.current_wallet = None

def login_page():
    # Apply custom page design
    st.set_page_config(page_title="Rugg Dashboard 🚀", page_icon="🦄", layout="centered")
    apply_custom_styles()

    if st.session_state.logged_in:
        display_launch_dashboard()
        return

    # Header Section
    colored_header(
        label="Welcome to the Rugg Dashboard 🚀",
        description="Securely log in with your Solana Wallet to get started.",
        color_name="violet-80",
    )
    
    # Rain animation for extra flair
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
                st.session_state.logged_in = True
                st.session_state.current_wallet = wallet
                add_participant(wallet)
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

def add_participant(wallet):
    if wallet not in [p['wallet'] for p in st.session_state.participants]:
        st.session_state.participants.append({
            'wallet': wallet,
            'joined_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'position': len(st.session_state.participants) + 1
        })

def display_launch_dashboard():
    st.title("Launch Dashboard 🚀")
    
    # Dashboard Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Your Position", next((p['position'] for p in st.session_state.participants if p['wallet'] == st.session_state.current_wallet), "N/A"))
    with col2:
        st.metric("Total Participants", len(st.session_state.participants))
    with col3:
        remaining = 1000 - len(st.session_state.participants)
        st.metric("Spots Remaining", f"{remaining}/1000")

    # Participants Table
    st.header("🎯 Secured Positions")
    if st.session_state.participants:
        df = pd.DataFrame(st.session_state.participants)
        st.dataframe(df, hide_index=True)
    
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
