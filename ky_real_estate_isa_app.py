import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Shaun's KY ISA", layout="wide", page_icon="🏠")

st.title("🗝️ Central Kentucky Real Estate ISA")
st.caption("AI Inside Sales Agent • Lexington • Richmond • Lancaster • Versailles")

# ====================== OPENAI SETUP ======================
if "openai_key" not in st.session_state:
    st.session_state.openai_key = os.getenv("OPENAI_API_KEY", "")

with st.sidebar:
    st.header("🔑 OpenAI Settings")
    api_key = st.text_input(
        "OpenAI API Key", 
        value=st.session_state.openai_key, 
        type="password"
    )
    
    if st.button("Save Key"):
        st.session_state.openai_key = api_key
        st.success("Key saved for this session!")
    
    model_choice = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    st.markdown("---")

# ====================== DATA ======================
if 'leads' not in st.session_state:
    st.session_state.leads = pd.DataFrame(columns=[
        'Date', 'Name', 'Phone', 'Type', 'Location', 'Budget', 'Status', 'Appointment'
    ])

if 'messages' not in st.session_state:
    st.session_state.messages = []

# ====================== HELPER FUNCTIONS ======================
def get_available_slots():
    slots = []
    current = datetime.now() + timedelta(days=1)
    while len(slots) < 8:
        if current.weekday() < 5:   # Mon-Fri
            for hour in [10, 13, 15]:
                slot = current.replace(hour=hour, minute=0)
                if slot > datetime.now():
                    slots.append(slot.strftime("%A, %b %d @ %I:%M %p"))
        current += timedelta(days=1)
    return slots

# ====================== NAVIGATION ======================
page = st.sidebar.selectbox("Go to", ["Lead Capture", "🤖 AI ISA Chat", "Dashboard"])

# ====================== LEAD CAPTURE ======================
if page == "Lead Capture":
    st.header("New Lead Capture")
    with st.form("lead_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone Number *")
            lead_type = st.selectbox("Lead Type", ["Buyer", "Seller"])
        with col2:
            location = st.selectbox("Area", ["Lexington", "Richmond", "Lancaster", "Versailles"])
            budget = st.number_input("Budget ($)", min_value=0, step=5000)
        
        submitted = st.form_submit_button("Save Lead")
        if submitted and name and phone:
            new_row = pd.DataFrame([{
                'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'Name': name,
                'Phone': phone,
                'Type': lead_type,
                'Location': location,
                'Budget': f"${budget:,}" if budget > 0 else "",
                'Status': 'New',
                'Appointment': ''
            }])
            st.session_state.leads = pd.concat([st.session_state.leads, new_row], ignore_index=True)
            st.success(f"✅ Lead for {name} saved successfully!")

# ====================== AI ISA CHAT ======================
elif page == "🤖 AI ISA Chat":
    st.header("🤖 AI ISA - Appointment Setter")
    
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hi! I'm Shaun's AI ISA. Thanks for your interest in Central Kentucky real estate. Are you looking to buy or sell?"
        })

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Type the lead's response..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        if not api_key or not api_key.startswith("sk-"):
            reply = "⚠️ Please enter a valid OpenAI API key in the sidebar."
        else:
            with st.spinner("AI ISA thinking..."):
                try:
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model=model_choice,
                        messages=st.session_state.messages,
                        temperature=0.75,
                        max_tokens=350
                    )
                    reply = response.choices[0].message.content
                except Exception as e:
                    reply = f"Error: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

# ====================== DASHBOARD ======================
elif page == "Dashboard":
    st.header("Leads Dashboard")
    if not st.session_state.leads.empty:
        st.dataframe(st.session_state.leads.sort_values('Date', ascending=False), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Leads", len(st.session_state.leads))
        with col2:
            st.download_button("Download CSV", 
                             st.session_state.leads.to_csv(index=False), 
                             "central_ky_leads.csv")
    else:
        st.info("No leads yet. Start by adding leads.")

st.caption("Built for Shaun • Central Kentucky Real Estate")