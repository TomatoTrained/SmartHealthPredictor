

import streamlit as st
from utils.database import init_db
from utils.auth import init_session_state, login, register, logout, require_auth, get_current_user

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'is_doctor' not in st.session_state:
    st.session_state.is_doctor = False


# Initialize database and session state
init_db()
init_session_state()

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 20px;
        height: 3rem;
        background-color: #0066cc;
        color: white;
    }
    .facility-image {
        border-radius: 10px;
        margin: 10px;
    }
    .service-item {
        margin-bottom: 10px;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("HealthCare Prediction System")

if not st.session_state.authenticated:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if login(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            email = st.text_input("Email")
            is_doctor = st.checkbox("Register as Doctor")
            specialty = st.text_input("Medical Specialty") if is_doctor else None
            register_submit = st.form_submit_button("Register")

            if register_submit:
                if register(new_username, new_password, email, is_doctor, specialty):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")

else:
    st.write(f"Welcome back, {'Dr. ' if st.session_state.is_doctor else ''}{st.session_state.username}!")

    # Facility images in a grid
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://images.unsplash.com/photo-1504813184591-01572f98c85f", 
                caption="Our Modern Facilities", use_container_width=True)
        st.image("https://images.unsplash.com/photo-1519494080410-f9aa76cb4283",
                caption="Advanced Technology", use_container_width=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1514416432279-50fac261c7dd",
                caption="Expert Care", use_container_width=True)
        st.image("https://images.unsplash.com/photo-1460672985063-6764ac8b9c74",
                caption="Patient Comfort", use_container_width=True)

    st.markdown("""
    ### Our Services
    - 🏥 Symptom Analysis
    - 👨‍⚕️ Doctor Consultations
    - 📅 Appointment Booking
    - 📊 Health Monitoring
    """)

    if st.button("Logout"):
        logout()
        st.rerun()
