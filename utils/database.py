from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# SQLite configuration - creates database in your project directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./smart_health.db"

# Engine configuration for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=True  # Shows SQL queries in console (remove in production)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)  # Added length constraint
    email = Column(String(100), unique=True, index=True)    # Added length constraint
    hashed_password = Column(String(255))                   # Store hashed passwords only
    is_doctor = Column(Boolean, default=False)
    specialty = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)  # Track account creation
    
    # Relationships with cascade delete rules
    health_records = relationship("HealthRecord", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    doctor_assessments = relationship("DoctorAssessment", back_populates="doctor", cascade="all, delete-orphan")

class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(DateTime, default=datetime.utcnow)
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    weight = Column(Float)
    blood_sugar = Column(Integer)
    oxygen_level = Column(Integer)
    sleep_hours = Column(Float)  # Changed to Float for partial hours
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="health_records")
    assessments = relationship("DoctorAssessment", back_populates="health_record", cascade="all, delete-orphan")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(DateTime, default=datetime.utcnow)
    symptoms = Column(JSON)
    predicted_disease = Column(String(100))  # Added length constraint
    confidence = Column(Float)
    severity = Column(Integer)
    recommendations = Column(JSON)
    
    # Relationship
    user = relationship("User", back_populates="predictions")

class DoctorAssessment(Base):
    __tablename__ = "doctor_assessments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    health_record_id = Column(Integer, ForeignKey("health_records.id", ondelete="CASCADE"))
    date = Column(DateTime, default=datetime.utcnow)
    assessment = Column(Text)
    recommendations = Column(Text)
    follow_up_date = Column(DateTime, nullable=True)
    prescription = Column(Text, nullable=True)  # Added prescription field
    
    # Relationships
    doctor = relationship("User", back_populates="doctor_assessments")
    health_record = relationship("HealthRecord", back_populates="assessments")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()