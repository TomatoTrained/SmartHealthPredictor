from utils.database import Base, engine, init_db
import streamlit as st
from utils.auth import init_session_state, login, register, logout
import streamlit.components.v1 as components

# Initialize database - this will create tables if they don't exist
init_db()

# Initialize session state
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
    .welcome-message {
        font-size: 1.5rem;
        margin-bottom: 2rem;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

st.title("HealthCare Prediction System")

if not st.session_state.authenticated:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login")

            if submit:
                if not username or not password:
                    st.error("Please fill in all fields")
                elif login(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        st.subheader("Create a New Account")
        with st.form("register_form"):
            new_username = st.text_input("Username", placeholder="Choose a username")
            new_password = st.text_input("Password", type="password", placeholder="Create a password")
            email = st.text_input("Email", placeholder="Enter your email")
            is_doctor = st.checkbox("Register as Doctor")
            specialty = st.text_input("Medical Specialty", placeholder="Your specialty") if is_doctor else None
            register_submit = st.form_submit_button("Register")

            if register_submit:
                if not new_username or not new_password or not email:
                    st.error("Please fill in all required fields")
                elif register(new_username, new_password, email, is_doctor, specialty):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")

else:
    st.markdown(f'<div class="welcome-message">Welcome back, {"Dr. " if st.session_state.is_doctor else ""}{st.session_state.username}!</div>', unsafe_allow_html=True)

    # Facility images in a grid
    st.subheader("Our Healthcare Facilities")
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://images.unsplash.com/photo-1504813184591-01572f98c85f", 
                caption="Our Modern Facilities", use_container_width=True, 
                output_format="auto")
        st.image("https://images.unsplash.com/photo-1519494080410-f9aa76cb4283",
                caption="Advanced Technology", use_container_width=True,
                output_format="auto")
    with col2:
        st.image("https://images.unsplash.com/photo-1514416432279-50fac261c7dd",
                caption="Expert Care", use_container_width=True,
                output_format="auto")
        st.image("https://images.unsplash.com/photo-1460672985063-6764ac8b9c74",
                caption="Patient Comfort", use_container_width=True,
                output_format="auto")

    st.subheader("Our Services")
    st.markdown("""
    <div class="service-item">🏥 Symptom Analysis</div>
    <div class="service-item">👨‍⚕️ Doctor Consultations</div>
    <div class="service-item">📅 Appointment Booking</div>
    <div class="service-item">📊 Health Monitoring</div>
    """, unsafe_allow_html=True)

    if st.button("Logout"):
        logout()
        st.rerun()
