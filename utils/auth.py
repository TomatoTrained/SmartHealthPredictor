import streamlit as st
from .database import User, get_db
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import os
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "is_doctor" not in st.session_state:
        st.session_state.is_doctor = False

def login(username: str, password: str) -> bool:
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if user and user.password == hash_password(password):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_id = user.id
        st.session_state.is_doctor = user.is_doctor
        return True
    return False

def register(username: str, password: str, email: str, is_doctor: bool = False, specialty: str = None) -> bool:
    db = next(get_db())
    if db.query(User).filter(User.username == username).first():
        return False

    new_user = User(
        username=username,
        password=hash_password(password),
        email=email,
        is_doctor=is_doctor,
        specialty=specialty
    )
    db.add(new_user)
    db.commit()
    return True

def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.is_doctor = False

def require_auth():
    if not st.session_state.authenticated:
        st.warning("Please login to access this feature")
        st.stop()

def get_current_user() -> User:
    if not st.session_state.authenticated:
        return None
    db = next(get_db())
    return db.query(User).filter(User.id == st.session_state.user_id).first()