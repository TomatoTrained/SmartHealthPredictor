from utils.database import SessionLocal, User
from typing import Optional
import streamlit as st
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_session_state():
    """Initialize Streamlit session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'is_doctor' not in st.session_state:
        st.session_state.is_doctor = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

def hash_password(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    return pwd_context.verify(plain_password, hashed_password)

def login(username: str, password: str) -> bool:
    """Authenticate a user"""
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    
    if user and user.verify_password(password):
        st.session_state.authenticated = True
        st.session_state.username = user.username
        st.session_state.is_doctor = user.is_doctor
        st.session_state.user_id = user.id
        return True
    return False

def register(username: str, password: str, email: str, is_doctor: bool = False, specialty: str = None) -> bool:
    """Register a new user"""
    db = next(get_db())
    if db.query(User).filter(User.username == username).first():
        return False
    
    new_user = User(
        username=username,
        email=email,
        is_doctor=is_doctor,
        specialty=specialty if is_doctor else None
    )
    new_user.set_password(password)
    
    db.add(new_user)
    db.commit()
    return True

def logout():
    """Clear the session state"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.is_doctor = False
    st.session_state.user_id = None

def require_auth():
    """Decorator to require authentication"""
    if not st.session_state.get('authenticated', False):
        st.warning("Please login to access this feature")
        st.stop()

def get_current_user():
    """Get current user from database"""
    if not st.session_state.authenticated:
        return None
    
    db = next(get_db())
    return db.query(User).filter(User.id == st.session_state.user_id).first()
