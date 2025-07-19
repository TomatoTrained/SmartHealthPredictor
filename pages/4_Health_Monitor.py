import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.auth import require_auth, get_current_user
from utils.database import SessionLocal, HealthRecord

# First verify authentication
require_auth()

# Get current user safely
current_user = get_current_user()
if current_user is None:
    st.error("User not found. Please login again.")
    st.stop()

st.title("Health Monitoring Dashboard")

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["Daily Metrics", "Trends Analysis", "Health Goals"])

with tab1:
    st.subheader("Today's Health Metrics")

    # Create three columns for input metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Blood Pressure & Heart Rate**")
        systolic = st.number_input("Systolic BP (mmHg)", 70, 200, 120)
        diastolic = st.number_input("Diastolic BP (mmHg)", 40, 130, 80)
        heart_rate = st.number_input("Heart Rate (bpm)", 40, 200, 75)

    with col2:
        st.markdown("**Body Metrics**")
        weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0, step=0.1)
        blood_sugar = st.number_input("Blood Sugar (mg/dL)", 50, 400, 100)
        oxygen_level = st.number_input("Oxygen Level (%)", 50, 100, 98)

    with col3:
        st.markdown("**Additional Notes**")
        mood = st.selectbox("Today's Mood", ["😊 Great", "🙂 Good", "😐 Okay", "😕 Not Good", "😢 Poor"])
        sleep_hours = st.number_input("Hours of Sleep", 0, 24, 8)
        notes = st.text_area("Health Notes", height=100)

    if st.button("Save Today's Metrics"):
        try:
            db = SessionLocal()
            new_record = HealthRecord(
                user_id=current_user.id,
                blood_pressure_systolic=systolic,
                blood_pressure_diastolic=diastolic,
                heart_rate=heart_rate,
                weight=weight,
                blood_sugar=blood_sugar,
                oxygen_level=oxygen_level,
                sleep_hours=sleep_hours,
                notes=notes
            )
            db.add(new_record)
            db.commit()
            st.success("Health metrics saved successfully!")
        except Exception as e:
            st.error(f"Error saving metrics: {str(e)}")
        finally:
            db.close()

with tab2:
    st.subheader("Health Trends Analysis")

    try:
        # Get historical data with parameterized query
        db = SessionLocal()
        records = pd.read_sql(
            "SELECT * FROM health_records WHERE user_id = :user_id ORDER BY date",
            db.bind,
            params={'user_id': current_user.id}
        )
        
        if not records.empty:
            # Convert date strings to datetime if needed
            if not pd.api.types.is_datetime64_any_dtype(records['date']):
                records['date'] = pd.to_datetime(records['date'])
            
            # Date range selector
            date_range = st.selectbox(
                "Select Time Range",
                ["Last 7 Days", "Last 30 Days", "Last 3 Months", "Last Year"]
            )

            ranges = {
                "Last 7 Days": 7,
                "Last 30 Days": 30,
                "Last 3 Months": 90,
                "Last Year": 365
            }

            cutoff_date = datetime.now() - timedelta(days=ranges[date_range])
            filtered_records = records[records['date'] >= cutoff_date]

            # Blood Pressure Trends
            fig_bp = go.Figure()
            fig_bp.add_trace(go.Scatter(
                x=filtered_records['date'],
                y=filtered_records['blood_pressure_systolic'],
                name="Systolic",
                line=dict(color='#FF9999', width=2)
            ))
            fig_bp.add_trace(go.Scatter(
                x=filtered_records['date'],
                y=filtered_records['blood_pressure_diastolic'],
                name="Diastolic",
                line=dict(color='#99FF99', width=2)
            ))
            fig_bp.update_layout(
                title="Blood Pressure Trends",
                xaxis_title="Date",
                yaxis_title="Blood Pressure (mmHg)",
                hovermode='x unified'
            )
            st.plotly_chart(fig_bp, use_container_width=True)

            # Create two columns for additional charts
            col1, col2 = st.columns(2)

            with col1:
                # Heart Rate Trends
                fig_hr = px.line(
                    filtered_records,
                    x='date',
                    y='heart_rate',
                    title="Heart Rate Trends"
                )
                fig_hr.update_traces(line_color='#FF9999')
                st.plotly_chart(fig_hr, use_container_width=True)

                # Blood Sugar Trends
                fig_bs = px.line(
                    filtered_records,
                    x='date',
                    y='blood_sugar',
                    title="Blood Sugar Trends"
                )
                fig_bs.update_traces(line_color='#FFB366')
                st.plotly_chart(fig_bs, use_container_width=True)

            with col2:
                # Weight Trends
                fig_weight = px.line(
                    filtered_records,
                    x='date',
                    y='weight',
                    title="Weight Trends"
                )
                fig_weight.update_traces(line_color='#9999FF')
                st.plotly_chart(fig_weight, use_container_width=True)

                # Oxygen Level Trends
                fig_oxygen = px.line(
                    filtered_records,
                    x='date',
                    y='oxygen_level',
                    title="Oxygen Level Trends"
                )
                fig_oxygen.update_traces(line_color='#66CC66')
                st.plotly_chart(fig_oxygen, use_container_width=True)

            # Statistical Insights
            st.subheader("Health Insights")
            latest = filtered_records.iloc[-1]

            # Create metrics with comparisons
            col1, col2, col3 = st.columns(3)

            with col1:
                bp_diff = latest['blood_pressure_systolic'] - filtered_records['blood_pressure_systolic'].mean()
                st.metric(
                    "Blood Pressure",
                    f"{int(latest['blood_pressure_systolic'])}/{int(latest['blood_pressure_diastolic'])}",
                    f"{bp_diff:.1f} from average"
                )

            with col2:
                hr_diff = latest['heart_rate'] - filtered_records['heart_rate'].mean()
                st.metric(
                    "Heart Rate",
                    f"{int(latest['heart_rate'])} bpm",
                    f"{hr_diff:.1f} from average"
                )

            with col3:
                weight_diff = latest['weight'] - filtered_records['weight'].mean()
                st.metric(
                    "Weight",
                    f"{latest['weight']:.1f} kg",
                    f"{weight_diff:.1f} from average"
                )
        else:
            st.info("Start tracking your health metrics to see trends and insights!")
    
    except Exception as e:
        st.error(f"Error loading health data: {str(e)}")
    finally:
        db.close()

with tab3:
    st.subheader("Health Goals")

    try:
        db = SessionLocal()
        records = pd.read_sql(
            "SELECT * FROM health_records WHERE user_id = :user_id ORDER BY date",
            db.bind,
            params={'user_id': current_user.id}
        )
        
        # Health goals section
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Set Your Health Targets")
            target_weight = st.number_input("Target Weight (kg)", 30.0, 200.0, 70.0, step=0.1)
            target_bp = st.number_input("Target Blood Pressure (Systolic)", 90, 140, 120)
            target_hr = st.number_input("Target Heart Rate (bpm)", 60, 100, 70)

        with col2:
            if not records.empty:
                latest = records.iloc[-1]
                st.markdown("### Progress Tracking")

                # Weight progress
                weight_progress = ((target_weight - latest['weight']) / target_weight) * 100
                st.write("Weight Goal Progress:")
                st.progress(max(min(abs(weight_progress) / 100, 1.0), 0.0))
                st.write(f"Current: {latest['weight']:.1f} kg | Target: {target_weight:.1f} kg")

                # Blood pressure progress
                bp_progress = ((target_bp - latest['blood_pressure_systolic']) / target_bp) * 100
                st.write("Blood Pressure Goal Progress:")
                st.progress(max(min(abs(bp_progress) / 100, 1.0), 0.0))
                st.write(f"Current: {int(latest['blood_pressure_systolic'])} mmHg | Target: {target_bp} mmHg")

                # Heart rate progress
                hr_progress = ((target_hr - latest['heart_rate']) / target_hr) * 100
                st.write("Heart Rate Goal Progress:")
                st.progress(max(min(abs(hr_progress) / 100, 1.0), 0.0))
                st.write(f"Current: {int(latest['heart_rate'])} bpm | Target: {target_hr} bpm")
            else:
                st.info("Start tracking your health metrics to see progress towards your goals!")
    
    except Exception as e:
        st.error(f"Error loading health data: {str(e)}")
    finally:
        db.close()

# Health Tips and Recommendations
st.sidebar.title("Health Insights")
try:
    db = SessionLocal()
    records = pd.read_sql(
        "SELECT * FROM health_records WHERE user_id = :user_id ORDER BY date DESC LIMIT 1",
        db.bind,
        params={'user_id': current_user.id}
    )
    
    if not records.empty:
        latest = records.iloc[0]

        # BP Status
        bp_status = "Normal"
        if latest['blood_pressure_systolic'] >= 140 or latest['blood_pressure_diastolic'] >= 90:
            bp_status = "High"
        elif latest['blood_pressure_systolic'] <= 90 or latest['blood_pressure_diastolic'] <= 60:
            bp_status = "Low"

        st.sidebar.markdown(f"**Blood Pressure Status:** {bp_status}")

        # General Health Tips
        st.sidebar.markdown("### Health Tips")
        tips = [
            "🏃‍♂️ Regular exercise improves heart health",
            "🥗 Maintain a balanced diet",
            "💧 Stay hydrated (8 glasses/day)",
            "😴 Get 7-9 hours of sleep",
            "🧘‍♀️ Practice stress management"
        ]
        for tip in tips:
            st.sidebar.write(tip)
except Exception as e:
    st.sidebar.error("Couldn't load health insights")
finally:
    db.close()
