from utils.database import SessionLocal, User
from typing import Optional
import streamlit as st
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Generator

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_db() -> Generator[Session, None, None]:
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_session_state():
    """Initialize Streamlit session state variables"""
    defaults = {
        'authenticated': False,
        'username': None,
        'is_doctor': False,
        'user_id': None,
        'email': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

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
    
    if user and verify_password(password, user.hashed_password):
        st.session_state.update({
            'authenticated': True,
            'username': user.username,
            'is_doctor': user.is_doctor,
            'user_id': user.id,
            'email': user.email
        })
        return True
    return False

def register(username: str, password: str, email: str, is_doctor: bool = False, specialty: str = None) -> bool:
    """Register a new user"""
    db = next(get_db())
    
    # Check if username or email already exists
    if db.query(User).filter((User.username == username) | (User.email == email)).first():
        return False
    
    new_user = User(
        username=username,
        email=email,
        is_doctor=is_doctor,
        specialty=specialty if is_doctor else None
    )
    new_user.hashed_password = hash_password(password)
    
    try:
        db.add(new_user)
        db.commit()
        
        # Auto-login after registration
        login(username, password)
        return True
    except Exception as e:
        db.rollback()
        st.error(f"Registration failed: {str(e)}")
        return False

def logout():
    """Clear the session state"""
    st.session_state.update({
        'authenticated': False,
        'username': None,
        'is_doctor': False,
        'user_id': None,
        'email': None
    })

def require_auth():
    """Require authentication for protected routes"""
    if not st.session_state.get('authenticated', False):
        st.warning("Please login to access this feature")
        st.stop()

def get_current_user() -> Optional[User]:
    """Get current user from database"""
    if not st.session_state.authenticated or not st.session_state.user_id:
        return None
    
    db = next(get_db())
    return db.query(User).filter(User.id == st.session_state.user_id).first()
