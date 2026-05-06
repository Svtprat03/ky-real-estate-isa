import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from openai import OpenAI
import os
from dotenv import load_dotenv, set_key

# Load .env file if it exists
load_dotenv()

st.set_page_config(page_title="Shaun's KY Real Estate ISA", layout="wide", page_icon="🏠")
st.title("🗝️ Central Kentucky Lead & Referral Manager")
st.markdown("**AI ISA powered by OpenAI** — Qualifies leads and books appointments")

st.caption("Lexington Market: Median ≈ $329K – $357K • Balanced Inventory")

# ====================== API KEY MANAGEMENT ======================
def get_api_key():
    # First priority: .env file
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key
    
    # Second priority: Session state
    if "openai_api_key" in st.session_state:
        return st.session_state.openai_api_key
    return None

# Sidebar - API Key Setup
with st.sidebar:
    st.header("🔑 OpenAI API Key")
    
    current_key = get_api_key()
    if current_key:
        st.success("✅ API Key loaded from .env file")
    else:
        st.warning("No API Key saved yet")
    
    manual_key = st.text_input("Enter OpenAI API Key", type="password", value="")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Key to .env"):
            if manual_key.startswith("sk-"):
                set_key(".env", "OPENAI_API_KEY", manual_key)
                st.success("✅ Key saved to .env file!")
                st.rerun()
            else:
                st.error("Invalid key format")
    
    with col2:
        if st.button("Clear Saved Key"):
            if os.path.exists(".env"):
                os.remove(".env")
                st.success("Key file removed")
                st.rerun()

    model_choice = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    st.markdown("---")

# ====================== REST OF THE APP ======================
api_key = get_api_key()

# Data Initialization
if 'leads' not in st.session_state:
    st.session_state.leads = pd.DataFrame(columns=['Date', 'Name', 'Phone', 'Type', 'Location', 'Budget', 'Status', 'Referral_Source', 'Appointment'])

if 'messages' not in st.session_state:
    st.session_state.messages = []

def get_available_slots():
    slots = []
    current = datetime.now() + timedelta(days=1)
    while len(slots) < 10:
        if current.weekday() < 5:
            for hour in [10, 13, 15]:
                slot = current.replace(hour=hour, minute=0)
                if slot > datetime.now():
                    slots.append(slot.strftime("%A, %b %d @ %I:%M %p"))
        current += timedelta(days=1)
    return slots

# Navigation
page = st.sidebar.selectbox("Navigation", ["Lead Capture", "🤖 AI ISA Chat", "Dashboard"])

# ==================== LEAD CAPTURE ====================
if page == "Lead Capture":
    st.header("New Lead Capture")
    with st.form("lead_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone *")
            lead_type = st.selectbox("Type", ["Buyer", "Seller"])
        with col2:
            location = st.selectbox("Area", ["Lexington", "Richmond", "Lancaster", "Versailles"])
            budget = st.number_input("Budget ($)", min_value=0, step=5000)
        
        submitted = st.form_submit_button("Save Lead")
        if submitted and name and phone:
            new_lead = pd.DataFrame([{
                'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'Name': name, 'Phone': phone, 'Type': lead_type,
                'Location': location, 'Budget': f"${budget:,}",
                'Status': 'New', 'Referral_Source': '', 'Appointment': ''
            }])
            st.session_state.leads = pd.concat([st.session_state.leads, new_lead], ignore_index=True)
            st.success(f"✅ Lead for {name} saved!")

# ==================== AI ISA CHAT ====================
elif page == "🤖 AI ISA Chat":
    st.header("🤖 AI ISA Chat")
    
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": "Hi! I'm Shaun's AI ISA. Are you looking to buy or sell in Central Kentucky?"})

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Lead's reply..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        if api_key:
            with st.spinner("AI ISA thinking..."):
                try:
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model=model_choice,
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                        temperature=0.7,
                        max_tokens=400
                    )
                    reply = response.choices[0].message.content
                except Exception as e:
                    reply = f"❌ Error: {str(e)}"
        else:
            reply = "⚠️ Please enter and save your OpenAI API key in the sidebar first."

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

# ==================== DASHBOARD ====================
elif page == "Dashboard":
    st.header("Leads Dashboard")
    if not st.session_state.leads.empty:
        st.dataframe(st.session_state.leads, use_container_width=True)
        st.download_button("Download Leads", st.session_state.leads.to_csv(index=False), "leads.csv")
    else:
        st.info("No leads yet. Go to Lead Capture to add some.")

st.caption("App for Shaun • Central Kentucky Real Estate • API Key saved securely in .env")