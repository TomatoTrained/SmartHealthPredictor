import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.prediction import predict_disease, get_recommendations

require_auth()
current_user = get_current_user()

st.title("Symptom Checker")

# List of common symptoms
symptoms_list = [
    "fever", "cough", "fatigue", "headache", "nausea",
    "sensitivity_to_light", "chest_pain", "shortness_of_breath",
    "dizziness", "abdominal_pain", "vomiting", "joint_pain",
    "swelling", "stiffness", "rash", "itching", "redness",
    "sore_throat", "difficulty_swallowing", "swollen_glands"
]

st.write("Please select your symptoms:")

# Create columns for symptoms selection
selected_symptoms = []
cols = st.columns(2)

for i, symptom in enumerate(symptoms_list):
    if cols[i % 2].checkbox(symptom.replace("_", " ").title()):
        selected_symptoms.append(symptom)

if selected_symptoms:
    if st.button("Analyze Symptoms"):
        with st.spinner("Analyzing your symptoms..."):
            predictions = predict_disease(selected_symptoms, current_user.id if current_user else None)

            st.subheader("Analysis Results")
            for pred in predictions:
                with st.expander(f"{pred['disease']} - {pred['confidence']:.1f}% Match"):
                    st.write(f"Severity Level: {'🔴' * pred['severity']}")
                    st.write("Recommended Actions:")
                    if pred['severity'] <= 2:
                        st.write("- Rest and monitor symptoms")
                        st.write("- Over-the-counter medication may help")
                    else:
                        st.write("- Consult a healthcare professional")
                        st.write("- Seek immediate medical attention if symptoms worsen")

                    recommended_doctors = get_recommendations(pred['disease'])
                    if recommended_doctors:
                        st.write("Recommended Specialists:")
                        for doctor in recommended_doctors:
                            st.write(f"- Dr. {doctor['name']} ({doctor['specialty']})")
else:
    st.info("Please select at least one symptom")