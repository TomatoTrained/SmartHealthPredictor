import streamlit as st
import json
from utils.auth import require_auth

require_auth()

st.title("Our Medical Specialists")

# Load doctors data
with open("data/doctors.json", "r") as f:
    doctors_data = json.load(f)

# Custom CSS for doctor cards
st.markdown("""
<style>
.doctor-card {
    padding: 20px;
    border-radius: 10px;
    background-color: #f8f9fa;
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.doctor-image {
    border-radius: 50%;
    width: 150px;
    height: 150px;
    object-fit: cover;
}
</style>
""", unsafe_allow_html=True)

# Filter options
specialties = list(set(doc["specialty"] for doc in doctors_data["doctors"]))
selected_specialty = st.selectbox("Filter by Specialty", ["All"] + specialties)

# Display doctors
for doctor in doctors_data["doctors"]:
    if selected_specialty == "All" or doctor["specialty"] == selected_specialty:
        with st.container():
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(doctor["image"], width=150)
            
            with col2:
                st.subheader(doctor["name"])
                st.write(f"Specialty: {doctor['specialty']}")
                st.write(f"Experience: {doctor['experience']} years")
                st.write(f"Rating: {'⭐' * int(doctor['rating'])} ({doctor['rating']})")
                st.write("Available on: " + ", ".join(doctor["availability"]))
                
                if st.button(f"Book Appointment with {doctor['name']}", key=doctor["id"]):
                    st.session_state.selected_doctor = doctor
                    st.switch_page("pages/3_Appointments.py")
