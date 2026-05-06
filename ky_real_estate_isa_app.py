import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from openai import OpenAI

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Shaun's Central KY Real Estate",
    layout="wide",
    page_icon="🏠"
)

st.title("🗝️ Central Kentucky Real Estate ISA")
st.caption("Lexington • Richmond • Lancaster • Versailles | AI-Powered Lead System")

# ====================== OPENAI SETUP ======================
if "openai_key" not in st.session_state:
    st.session_state.openai_key = st.secrets.get("OPENAI_API_KEY", "")

api_key = st.session_state.openai_key

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Settings")
    mode = st.radio("App Mode", ["Full Internal App", "Landing Page Mode"], horizontal=True)
    
    if mode == "Full Internal App":
        page = st.selectbox("Navigation", [
            "Lead Capture", 
            "Website Embed Form", 
            "🤖 AI ISA Chat", 
            "Follow-up Generator", 
            "Dashboard"
        ])
    else:
        page = "Landing Page"
    
    model_choice = st.selectbox("AI Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    st.markdown("---")
    st.caption("Built for Shaun • Central Kentucky")

# ====================== DATA ======================
if 'leads' not in st.session_state:
    st.session_state.leads = pd.DataFrame(columns=[
        'Date', 'Name', 'Phone', 'Email', 'Type', 'Location', 'Budget', 'Status'
    ])

if 'messages' not in st.session_state:
    st.session_state.messages = []

# ====================== HELPER FUNCTIONS ======================
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

# ====================== LANDING PAGE ======================
if page == "Landing Page":
    st.header("Ready to Buy or Sell in Central Kentucky?")
    st.subheader("Let Shaun help you make the right move in the Bluegrass Region.")
    
    with st.form("landing_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone Number *")
        with col2:
            email = st.text_input("Email Address")
            lead_type = st.selectbox("I want to", ["Buy a Home", "Sell a Home", "Both"])
        
        location = st.selectbox("Preferred Area", ["Lexington", "Richmond", "Lancaster", "Versailles", "Central KY"])
        budget = st.number_input("Budget / Price Range ($)", min_value=0, step=10000)
        
        if st.form_submit_button("Submit - Get Help Now", type="primary"):
            if name and phone:
                new_lead = pd.DataFrame([{
                    'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'Name': name, 'Phone': phone, 'Email': email,
                    'Type': lead_type, 'Location': location,
                    'Budget': f"${budget:,}" if budget > 0 else "",
                    'Status': 'New'
                }])
                st.session_state.leads = pd.concat([st.session_state.leads, new_lead], ignore_index=True)
                st.success("✅ Thank you! Shaun or his team will contact you shortly.")
                st.balloons()
            else:
                st.error("Name and Phone are required.")

# ====================== WEBSITE EMBED FORM ======================
elif page == "Website Embed Form":
    st.header("Professional Website Lead Form")
    st.info("You can embed this form on your website.")
    
    with st.form("embed_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone *")
            email = st.text_input("Email")
        with col2:
            lead_type = st.selectbox("Interested In", ["Buying", "Selling", "Both"])
            location = st.selectbox("Area", ["Lexington", "Richmond", "Lancaster", "Versailles"])
            budget = st.number_input("Budget / Asking Price ($)", min_value=0)
        
        if st.form_submit_button("Submit Lead", type="primary"):
            if name and phone:
                new_lead = pd.DataFrame([{
                    'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'Name': name, 'Phone': phone, 'Email': email,
                    'Type': lead_type, 'Location': location,
                    'Budget': f"${budget:,}" if budget > 0 else "",
                    'Status': 'New'
                }])
                st.session_state.leads = pd.concat([st.session_state.leads, new_lead], ignore_index=True)
                st.success("✅ Lead submitted successfully!")

# ====================== LEAD CAPTURE (Internal) ======================
elif page == "Lead Capture":
    st.header("Internal Lead Capture")
    with st.form("internal_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone *")
            email = st.text_input("Email")
        with col2:
            lead_type = st.selectbox("Type", ["Buyer", "Seller", "Both"])
            location = st.selectbox("Area", ["Lexington", "Richmond", "Lancaster", "Versailles"])
            budget = st.number_input("Budget ($)", min_value=0, step=5000)
        
        if st.form_submit_button("Save Lead"):
            if name and phone:
                new_lead = pd.DataFrame([{
                    'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'Name': name, 'Phone': phone, 'Email': email,
                    'Type': lead_type, 'Location': location,
                    'Budget': f"${budget:,}" if budget > 0 else "",
                    'Status': 'New'
                }])
                st.session_state.leads = pd.concat([st.session_state.leads, new_lead], ignore_index=True)
                st.success(f"Lead for {name} saved!")

# ====================== AI ISA CHAT ======================
elif page == "🤖 AI ISA Chat":
    st.header("🤖 AI ISA Chat - Appointment Setter")
    
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": "Hi! I'm Shaun's AI ISA. Are you looking to buy or sell in Central Kentucky?"})

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Lead's response..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        if api_key:
            with st.spinner("AI ISA thinking..."):
                try:
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model=model_choice,
                        messages=st.session_state.messages,
                        temperature=0.7
                    )
                    reply = response.choices[0].message.content
                except Exception as e:
                    reply = f"Error: {e}"
        else:
            reply = "Please configure OpenAI API key in Streamlit Secrets."

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

# ====================== FOLLOW-UP GENERATOR ======================
elif page == "Follow-up Generator":
    st.header("AI Follow-up Message Generator")
    
    if not st.session_state.leads.empty:
        lead_name = st.selectbox("Select Lead", st.session_state.leads['Name'].tolist())
        selected = st.session_state.leads[st.session_state.leads['Name'] == lead_name].iloc[0]
        
        followup_type = st.selectbox("Follow-up Type", [
            "Initial Contact", 
            "After CMA", 
            "Objection Handling", 
            "Appointment Reminder"
        ])
        
        if st.button("Generate Email & SMS"):
            prompt = f"""Write professional but warm follow-up messages for this real estate lead:
            Name: {selected['Name']}
            Type: {selected['Type']}
            Area: {selected['Location']}
            Budget: {selected['Budget']}
            
            Type: {followup_type}
            
            Return:
            1. Short SMS version (under 160 characters)
            2. Professional Email version"""
            
            with st.spinner("Generating..."):
                try:
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model=model_choice,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.write(response.choices[0].message.content)
                except:
                    st.error("Error generating messages. Check API key.")
    else:
        st.info("No leads yet. Add some leads first.")

# ====================== DASHBOARD ======================
elif page == "Dashboard":
    st.header("Leads Dashboard")
    if not st.session_state.leads.empty:
        st.dataframe(st.session_state.leads.sort_values('Date', ascending=False), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Leads", len(st.session_state.leads))
        with col2:
            st.download_button(
                "Download Leads as CSV",
                st.session_state.leads.to_csv(index=False),
                "central_ky_leads.csv"
            )
    else:
        st.info("No leads yet.")

st.caption("Central Kentucky Real Estate ISA App • Powered by OpenAI")