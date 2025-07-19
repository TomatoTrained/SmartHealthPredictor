from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from datetime import datetime
import os
import atexit
from typing import Optional, List, Dict, Any
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database configuration
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///smart_health.db")

# Engine configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
    pool_pre_ping=True,
    echo=False
)

# Session factory
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
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_records = relationship("HealthRecord", 
                                back_populates="user", 
                                cascade="all, delete-orphan")
    
    patient_predictions = relationship("Prediction", 
                                     foreign_keys="[Prediction.user_id]",
                                     back_populates="user",
                                     cascade="all, delete-orphan")
    
    doctor_reviews = relationship("Prediction",
                                foreign_keys="[Prediction.reviewed_by]",
                                back_populates="reviewing_doctor")
    
    doctor_assessments = relationship("DoctorAssessment", 
                                    foreign_keys="[DoctorAssessment.doctor_id]",
                                    back_populates="doctor",
                                    cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

class HealthRecord(Base):
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    temperature = Column(Float)
    blood_sugar = Column(Integer)
    oxygen_level = Column(Integer)
    sleep_hours = Column(Float)
    notes = Column(Text)
    bmi = Column(Float)
    
    user = relationship("User", back_populates="health_records")
    assessments = relationship("DoctorAssessment", 
                             back_populates="health_record", 
                             cascade="all, delete-orphan")

    def calculate_bmi(self):
        if self.height and self.weight:
            self.bmi = round(self.weight / ((self.height / 100) ** 2), 1)
        return self.bmi

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
    is_reviewed = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", foreign_keys=[user_id], back_populates="patient_predictions")
    reviewing_doctor = relationship("User", foreign_keys=[reviewed_by], back_populates="doctor_reviews")

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
    prescription_issued = Column(Boolean, default=False)
    
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_assessments")
    health_record = relationship("HealthRecord", foreign_keys=[health_record_id], back_populates="assessments")

def clear_database_sessions():
    """Clear all database sessions"""
    SessionLocal.remove()

def init_db():
    """Initialize the database and create tables"""
    try:
        Base.metadata.drop_all(bind=engine)  # Drop existing tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise

def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register cleanup at exit
atexit.register(clear_database_sessions)

# Initialize database when module is imported
init_db()
