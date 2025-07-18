import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.auth import require_auth, get_current_user
from utils.database import SessionLocal, User, HealthRecord, DoctorAssessment, Prediction

require_auth()
current_user = get_current_user()

# Verify if the user is a doctor
if not current_user or not current_user.is_doctor:
    st.error("This page is only accessible to doctors")
    st.stop()

st.title("Doctor's Dashboard")

# Get list of patients
db = SessionLocal()
patients = db.query(User).filter(User.is_doctor == False).all()

# Patient selector
selected_patient = st.selectbox(
    "Select Patient",
    options=patients,
    format_func=lambda x: f"{x.username} (ID: {x.id})"
)

if selected_patient:
    st.header(f"Patient: {selected_patient.username}")
    
    # Get patient's health records
    health_records = (
        db.query(HealthRecord)
        .filter(HealthRecord.user_id == selected_patient.id)
        .order_by(HealthRecord.date.desc())
        .all()
    )
    
    # Get patient's predictions
    predictions = (
        db.query(Prediction)
        .filter(Prediction.user_id == selected_patient.id)
        .order_by(Prediction.date.desc())
        .all()
    )

    tab1, tab2, tab3 = st.tabs(["Health Records", "Symptom History", "Add Assessment"])

    with tab1:
        st.subheader("Recent Health Records")
        if health_records:
            for record in health_records[:5]:  # Show last 5 records
                with st.expander(f"Record from {record.date.strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Blood Pressure: {record.blood_pressure_systolic}/{record.blood_pressure_diastolic}")
                        st.write(f"Heart Rate: {record.heart_rate} bpm")
                        st.write(f"Weight: {record.weight} kg")
                    with col2:
                        st.write(f"Blood Sugar: {record.blood_sugar} mg/dL")
                        st.write(f"Oxygen Level: {record.oxygen_level}%")
                        st.write(f"Sleep Hours: {record.sleep_hours}")
                    if record.notes:
                        st.write("Notes:", record.notes)
                    
                    # Show existing assessments
                    assessments = db.query(DoctorAssessment).filter(
                        DoctorAssessment.health_record_id == record.id
                    ).all()
                    
                    if assessments:
                        st.write("Previous Assessments:")
                        for assessment in assessments:
                            st.info(
                                f"""
                                By Dr. {assessment.doctor.username} on {assessment.date.strftime('%Y-%m-%d')}:
                                Assessment: {assessment.assessment}
                                Recommendations: {assessment.recommendations}
                                Follow-up: {assessment.follow_up_date.strftime('%Y-%m-%d') if assessment.follow_up_date else 'Not scheduled'}
                                """
                            )
        else:
            st.info("No health records available for this patient")

    with tab2:
        st.subheader("Symptom Analysis History")
        if predictions:
            for pred in predictions:
                with st.expander(f"Analysis from {pred.date.strftime('%Y-%m-%d %H:%M')}"):
                    st.write("Symptoms:", ", ".join(eval(pred.symptoms)))
                    st.write(f"Predicted Condition: {pred.predicted_disease}")
                    st.write(f"Confidence: {pred.confidence:.1f}%")
                    st.write(f"Severity Level: {'🔴' * pred.severity}")
        else:
            st.info("No symptom analysis history available")

    with tab3:
        st.subheader("Add New Assessment")
        
        # Select health record to assess
        record_to_assess = st.selectbox(
            "Select Health Record",
            options=health_records,
            format_func=lambda x: f"Record from {x.date.strftime('%Y-%m-%d %H:%M')}",
            key="record_selector"
        )
        
        if record_to_assess:
            assessment = st.text_area("Assessment", height=100)
            recommendations = st.text_area("Recommendations", height=100)
            follow_up_date = st.date_input(
                "Schedule Follow-up",
                min_value=datetime.now().date(),
                value=datetime.now().date() + timedelta(days=7)
            )
            
            if st.button("Submit Assessment"):
                try:
                    new_assessment = DoctorAssessment(
                        doctor_id=current_user.id,
                        health_record_id=record_to_assess.id,
                        assessment=assessment,
                        recommendations=recommendations,
                        follow_up_date=follow_up_date
                    )
                    db.add(new_assessment)
                    db.commit()
                    st.success("Assessment submitted successfully!")
                except Exception as e:
                    st.error(f"Error submitting assessment: {str(e)}")

# Close database connection
db.close()
