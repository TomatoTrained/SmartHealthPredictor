import pandas as pd
import numpy as np
import json
from datetime import datetime
from .database import SessionLocal, Prediction

def load_symptoms_data():
    return pd.read_csv("data/symptoms.csv")

def predict_disease(symptoms, user_id=None):
    df = load_symptoms_data()

    # Simple matching algorithm
    matches = []
    for _, row in df.iterrows():
        score = sum(1 for s in symptoms if s in [row['symptom_1'], row['symptom_2'], row['symptom_3']])
        if score > 0:
            matches.append({
                'disease': row['disease'],
                'confidence': (score / 3) * 100,
                'severity': row['severity']
            })

    # Sort by confidence
    matches.sort(key=lambda x: x['confidence'], reverse=True)
    top_matches = matches[:3]

    # Store prediction in database if user is logged in
    if user_id:
        db = SessionLocal()
        try:
            prediction = Prediction(
                user_id=user_id,
                symptoms=json.dumps(symptoms),
                predicted_disease=top_matches[0]['disease'],
                confidence=top_matches[0]['confidence'],
                severity=top_matches[0]['severity'],
                recommendations=json.dumps(get_recommendations(top_matches[0]['disease']))
            )
            db.add(prediction)
            db.commit()
        finally:
            db.close()

    return top_matches

def get_recommendations(disease):
    with open("data/doctors.json", "r") as f:
        doctors_data = json.load(f)

    # Simple matching based on specialty
    recommended_doctors = []
    disease_specialty_map = {
        "Heart Disease": "Cardiology",
        "Migraine": "Neurology",
        "Allergic Reaction": "Dermatology"
    }

    specialty = disease_specialty_map.get(disease, "General Medicine")

    for doctor in doctors_data["doctors"]:
        if doctor["specialty"] == specialty:
            recommended_doctors.append(doctor)

    return recommended_doctors