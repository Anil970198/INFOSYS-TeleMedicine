import pandas as pd
import spacy
import streamlit as st
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os

# Load SpaCy Model (Optional if you want to process the conversation)
nlp = spacy.load("en_core_web_sm")

# Google Calendar Setup
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

# Authenticate and initialize Google Calendar API
service = authenticate_google_calendar()

# Function to Process Conversations (Optional, if you want to flag based on conversation)
def process_conversation(conversation):
    doc = nlp(conversation)
    flagged_words = [word for word in ['stress', 'anxiety', 'depression', 'suicide', 'sad', 'hopeless'] if word in conversation.lower()]
    risk = "High Risk" if flagged_words else "Low Risk"
    return risk, flagged_words

# Function to Schedule a Meeting
from datetime import datetime

from datetime import datetime, date, time as time_obj

from datetime import datetime, timedelta

from datetime import datetime, timedelta

def schedule_meeting(patient_name, selected_date, selected_time):
    try:
        # Convert selected_date (string) to datetime.date if necessary
        if isinstance(selected_date, str):
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

        # Convert selected_time (string) to datetime.time if necessary
        if isinstance(selected_time, str):
            selected_time = datetime.strptime(selected_time, "%H:%M:%S").time()

        # Combine date and time properly
        start_datetime = datetime.combine(selected_date, selected_time)
        end_datetime = start_datetime + timedelta(minutes=30)  # Adds 30 minutes for the meeting duration

        event = {
            'summary': f'Meeting with {patient_name}',
            'description': 'Follow-up meeting for mental health check-in.',
            'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'IST'},
            'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'IST'},
        }

        print("Generated Event JSON:", event)  # Debugging

        service.events().insert(calendarId='primary', body=event).execute()
        st.success(f"Meeting scheduled for {patient_name} on {selected_date} at {selected_time}.")
    except Exception as e:
        st.error(f"Error scheduling meeting: {e}")
        print("Error scheduling meeting:", e)




# Streamlit App
st.title("Mental Health Risk Dashboard")

# Upload Dataset
uploaded_file = st.file_uploader("Upload Patient Data (CSV)", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Process Risk Levels and Add Flags for High-Risk Patients
    df['Risk_Label'] = df.apply(lambda row: 'High Risk' if row['total_risk_score'] > 0.7 else 'Low Risk', axis=1)

    # Display Filter Options
    st.sidebar.header("Filter Options")
    risk_filter = st.sidebar.selectbox("Filter by Risk Level", ["All", "High Risk", "Low Risk"])

    # Filter Data
    if risk_filter == "High Risk":
        filtered_df = df[df['Risk_Label'] == "High Risk"]
    elif risk_filter == "Low Risk":
        filtered_df = df[df['Risk_Label'] == "Low Risk"]
    else:
        filtered_df = df

    # Display Data
    st.write("### Patient Data")
    st.dataframe(filtered_df)

    # Schedule Meetings for High-Risk Patients
    st.write("### Schedule Meetings")
    for _, row in filtered_df.iterrows():
        if row['Risk_Label'] == "High Risk":
            with st.expander(f"Schedule for Patient ID: {row['patient_id']}"):
                date = st.date_input(f"Meeting Date for Patient ID: {row['patient_id']}")
                time = st.time_input(f"Meeting Time for Patient ID: {row['patient_id']}")
                if st.button(f"Schedule Meeting for Patient ID: {row['patient_id']}"):
                    schedule_meeting(row['patient_id'], date.isoformat(), time.isoformat())

else:
    st.info("Please upload a dataset to begin.")
