from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from datetime import datetime
import os
import atexit
from typing import Optional, List, Dict, Any

# Database configuration with environment variable fallback
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"sqlite:///{os.path.join(os.path.dirname(__file__), 'smart_health.db')}"
)

class DatabaseConfig:
    """Centralized database configuration"""
    POOL_SIZE = 5
    MAX_OVERFLOW = 10
    POOL_TIMEOUT = 30
    POOL_RECYCLE = 3600

# Engine configuration with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
    pool_size=DatabaseConfig.POOL_SIZE,
    max_overflow=DatabaseConfig.MAX_OVERFLOW,
    pool_timeout=DatabaseConfig.POOL_TIMEOUT,
    pool_recycle=DatabaseConfig.POOL_RECYCLE,
    echo=False  # Set to True for debugging
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
    """User model with enhanced validation fields"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_doctor = Column(Boolean, default=False)
    specialty = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_records = relationship("HealthRecord", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    doctor_assessments = relationship("DoctorAssessment", back_populates="doctor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', is_doctor={self.is_doctor})>"

class HealthRecord(Base):
    """Comprehensive health record model with additional fields"""
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    weight = Column(Float)
    height = Column(Float)  # Added for BMI calculation
    temperature = Column(Float)  # Added body temperature
    blood_sugar = Column(Integer)
    oxygen_level = Column(Integer)
    sleep_hours = Column(Float)
    notes = Column(Text)
    bmi = Column(Float)  # Calculated field
    
    # Relationships
    user = relationship("User", back_populates="health_records")
    assessments = relationship("DoctorAssessment", back_populates="health_record", cascade="all, delete-orphan")

    def calculate_bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.height and self.weight:
            return round(self.weight / ((self.height / 100) ** 2), 1)
        return None

class Prediction(Base):
    """Disease prediction model with enhanced fields"""
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
    
    # Relationships
    user = relationship("User", back_populates="predictions", foreign_keys=[user_id])
    reviewing_doctor = relationship("User", foreign_keys=[reviewed_by])

class DoctorAssessment(Base):
    """Doctor assessment model with prescription support"""
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
    
    # Relationships
    doctor = relationship("User", back_populates="doctor_assessments")
    health_record = relationship("HealthRecord", back_populates="assessments")

def init_db():
    """Initialize the database and create tables with error handling"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise

def get_db():
    """Generator function to get a database session with proper cleanup"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def cleanup():
    """Cleanup function to close all database connections"""
    try:
        SessionLocal.remove()
        engine.dispose()
        print("✅ Database connections cleaned up successfully")
    except Exception as e:
        print(f"❌ Error cleaning up database connections: {e}")

# Register cleanup to run at program exit
atexit.register(cleanup)

# Initialize database when module is imported
if __name__ == "__main__":
    init_db()
