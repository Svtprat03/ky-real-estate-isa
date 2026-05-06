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
st.caption("Lexington • Richmond • Lancaster • Versailles | AI Lead System")

# ====================== OPENAI SETUP ======================
api_key = st.secrets.get("OPENAI_API_KEY", "") if "OPENAI_API_KEY" in st.secrets else st.session_state.get("openai_key", "")

with st.sidebar:
    st.header("⚙️ Settings")
    page = st.selectbox("Navigation", [
        "Lead Capture",
        "Website Embed Form",
        "🤖 AI ISA Chat",
        "Follow-up Generator",
        "Dashboard"
    ])
    model_choice = st.selectbox("AI Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    st.markdown("---")
    st.caption("Built for Shaun • Central Kentucky Real Estate")

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

# ====================== LEAD CAPTURE ======================
if page == "Lead Capture":
    st.header("Internal Lead Capture")
    with st.form("lead_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone *")
            email = st.text_input("Email")
        with col2:
            lead_type = st.selectbox("Lead Type", ["Buyer", "Seller", "Both"])
            location = st.selectbox("Area", ["Lexington", "Richmond", "Lancaster", "Versailles"])
            budget = st.number_input("Budget / Price ($)", min_value=0, step=5000)
        
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
                st.success(f"✅ Lead for {name} saved successfully!")

# ====================== WEBSITE EMBED FORM ======================
elif page == "Website Embed Form":
    st.header("Professional Website Lead Capture Form")
    st.info("This form can be embedded on your website.")
    
    with st.form("embed_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone Number *")
            email = st.text_input("Email")
        with col2:
            lead_type = st.selectbox("Interested In", ["Buying", "Selling", "Both"])
            location = st.selectbox("Preferred Area", ["Lexington", "Richmond", "Lancaster", "Versailles"])
            budget = st.number_input("Budget / Price Range ($)", min_value=0, step=5000)
        
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
                st.success("✅ Lead received! Thank you.")

# ====================== AI ISA CHAT ======================
elif page == "🤖 AI ISA Chat":
    st.header("🤖 AI ISA - Appointment Setter")
    
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": "Hi! I'm Shaun's AI ISA. Are you looking to buy or sell in Central Kentucky?"})

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Type the lead's response..."):
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
            reply = "Please add your OpenAI API key in Streamlit Secrets."

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

# ====================== ENHANCED FOLLOW-UP GENERATOR ======================
elif page == "Follow-up Generator":
    st.header("📧 AI Follow-up Message Generator")
    st.markdown("Generate highly personalized Email & SMS follow-ups")

    if st.session_state.leads.empty:
        st.warning("No leads available. Add leads first.")
    else:
        # Improved lead selector
        lead_list = st.session_state.leads.copy()
        lead_list['Display'] = lead_list.apply(
            lambda x: f"{x['Name']} ({x['Type']} - {x['Location']})", axis=1)
        
        selected_display = st.selectbox("Select a lead", lead_list['Display'].tolist())
        selected_lead = st.session_state.leads[lead_list['Display'] == selected_display].iloc[0]

        followup_type = st.selectbox("Follow-up Type", [
            "Initial Follow-up (First Contact)",
            "After Sending CMA / Market Analysis",
            "Objection Handling",
            "Appointment Confirmation / Reminder",
            "Nurture / No Response Yet",
            "Price Reduction / Motivation Boost"
        ])

        additional_context = st.text_area("Additional Context (helps AI personalize)", 
                                        placeholder="e.g. They just got a new job, concerned about interest rates, etc.")

        if st.button("Generate Email + SMS", type="primary"):
            if not api_key:
                st.error("OpenAI API key required.")
            else:
                with st.spinner("Generating personalized messages..."):
                    prompt = f"""Create natural, professional real estate follow-up messages.

Lead Information:
- Name: {selected_lead['Name']}
- Type: {selected_lead['Type']}
- Area: {selected_lead['Location']}
- Budget: {selected_lead['Budget']}
- Status: {selected_lead['Status']}
- Context: {additional_context or 'No extra context'}

Follow-up Type: {followup_type}

Please provide:
1. **SMS Version** (under 160 characters) - friendly and conversational
2. **Email Version** - warm, professional, with strong call to action

Make it feel personal and specific."""

                    try:
                        client = OpenAI(api_key=api_key)
                        response = client.chat.completions.create(
                            model=model_choice,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.75,
                            max_tokens=700
                        )
                        st.success("✅ Messages Generated Successfully!")
                        st.write(response.choices[0].message.content)
                    except Exception as e:
                        st.error(f"Error: {e}")

# ====================== DASHBOARD ======================
elif page == "Dashboard":
    st.header("Leads Dashboard")
    if not st.session_state.leads.empty:
        st.dataframe(
            st.session_state.leads.sort_values('Date', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Leads", len(st.session_state.leads))
        with col2:
            st.download_button(
                label="📥 Download Leads CSV",
                data=st.session_state.leads.to_csv(index=False),
                file_name="central_ky_leads.csv",
                mime="text/csv"
            )
    else:
        st.info("No leads yet. Start capturing leads!")

st.caption("Central Kentucky Real Estate ISA App • Enhanced Follow-up Generator")