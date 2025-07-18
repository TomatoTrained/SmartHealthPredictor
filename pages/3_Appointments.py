import streamlit as st
from datetime import datetime, timedelta
from utils.auth import require_auth
import json

require_auth()

st.title("Book Appointment")

# Load doctors data
with open("data/doctors.json", "r") as f:
    doctors_data = json.load(f)

# Get selected doctor from session state or show selector
if "selected_doctor" not in st.session_state:
    doctor_names = [doc["name"] for doc in doctors_data["doctors"]]
    selected_name = st.selectbox("Select Doctor", doctor_names)
    selected_doctor = next(doc for doc in doctors_data["doctors"] if doc["name"] == selected_name)
else:
    selected_doctor = st.session_state.selected_doctor
    st.session_state.selected_doctor = None  # Clear selection after use

st.subheader(f"Book Appointment with {selected_doctor['name']}")
st.write(f"Specialty: {selected_doctor['specialty']}")

# Date selection
available_dates = []
today = datetime.now()
for i in range(14):  # Next 14 days
    date = today + timedelta(days=i)
    if date.strftime("%A") in selected_doctor["availability"]:
        available_dates.append(date.strftime("%Y-%m-%d"))

selected_date = st.selectbox("Select Date", available_dates)

# Time slots
time_slots = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
selected_time = st.selectbox("Select Time", time_slots)

# Appointment reason
reason = st.text_area("Reason for Visit", height=100)

# Confirmation
if st.button("Confirm Appointment"):
    appointment = {
        "doctor": selected_doctor["name"],
        "date": selected_date,
        "time": selected_time,
        "reason": reason
    }
    
    # In a real application, save to database
    st.success(f"""
    Appointment Confirmed!
    
    Doctor: {selected_doctor['name']}
    Date: {selected_date}
    Time: {selected_time}
    
    Please arrive 15 minutes before your appointment.
    """)
