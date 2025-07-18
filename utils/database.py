from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from datetime import datetime
import os
import atexit

# Database configuration
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_health.db")

# Engine configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
    pool_pre_ping=True,  # Check connections before using them
    echo=False  # Disable in production
)

# Session factory with scoped sessions for thread safety
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_doctor = Column(Boolean, default=False)
    specialty = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    health_records = relationship("HealthRecord", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    doctor_assessments = relationship("DoctorAssessment", back_populates="doctor", cascade="all, delete-orphan")

class HealthRecord(Base):
    __tablename__ = "health_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    weight = Column(Float)
    blood_sugar = Column(Integer)
    oxygen_level = Column(Integer)
    sleep_hours = Column(Float)
    notes = Column(Text)
    
    user = relationship("User", back_populates="health_records")
    assessments = relationship("DoctorAssessment", back_populates="health_record", cascade="all, delete-orphan")

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    symptoms = Column(JSON)
    predicted_disease = Column(String(100))
    confidence = Column(Float)
    severity = Column(Integer)
    recommendations = Column(JSON)
    
    user = relationship("User", back_populates="predictions")

class DoctorAssessment(Base):
    __tablename__ = "doctor_assessments"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    health_record_id = Column(Integer, ForeignKey("health_records.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    assessment = Column(Text)
    recommendations = Column(Text)
    follow_up_date = Column(DateTime, nullable=True)
    prescription = Column(Text, nullable=True)
    
    doctor = relationship("User", back_populates="doctor_assessments")
    health_record = relationship("HealthRecord", back_populates="assessments")

def init_db():
    """Initialize the database and create tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Cleanup function
def cleanup():
    """Close all database connections"""
    SessionLocal.remove()
    engine.dispose()

# Register cleanup
atexit.register(cleanup)

# Initialize database when module is imported
init_db()
