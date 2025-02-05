
# Mental Health Consultation System


This project analyzes doctor-patient conversations to detect emotional distress using natural language processing (NLP). It helps healthcare professionals identify at-risk patients and prioritize consultations effectively. The system allows filtering patients into high and low-risk categories and integrates with Google Calendar for scheduling follow-up sessions.

## Features

- **Patient Sentiment Analysis:** Uses NLP techniques to analyze doctor-patient conversations and detect emotional distress.
- **Risk Categorization:** Classifies patients as high-risk or low-risk based on sentiment and keyword analysis.
- **Interactive Dashboard:** A Streamlit-powered interface for filtering and reviewing patient data.
- **Meeting Scheduling:** Integrates with Google Calendar to schedule follow-up consultations for high-risk patients.
- **User-Friendly Interface:** Simple and intuitive layout for healthcare professionals to access insights quickly.




## Core Code Components

### 1. Text Preprocessing

``` python

import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Initialize stopwords and lemmatizer
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Function to clean text
def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text.lower())  # Remove punctuation
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return ' '.join(tokens)

```
### 2. Sentiment and Emotion Analysis

``` python
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Initialize sentiment analyzer
vader_analyzer = SentimentIntensityAnalyzer()

# Map sentiment scores to emotions
def map_sentiment_to_emotion(polarity):
    if polarity >= 0.5:
        return "Joy"
    elif 0 < polarity < 0.5:
        return "Neutral"
    elif -0.5 <= polarity < 0:
        return "Sadness"
    else:
        return "Anger"

# Analyze emotions in text
def analyze_emotions(text):
    scores = vader_analyzer.polarity_scores(text)
    return map_sentiment_to_emotion(scores['compound'])
```

### 3. Identifying Concerns and Reassurances

``` python
concern_keywords = ["worse", "difficult", "struggle", "pain", "scared", "fear"]
reassurance_keywords = ["better", "normal", "okay", "support", "safe"]

def analyze_conversation(conversation):
    concerns = [sent for sent in conversation.split('.') if any(kw in sent for kw in concern_keywords)]
    reassurances = [sent for sent in conversation.split('.') if any(kw in sent for kw in reassurance_keywords)]
    return {"Concerns": concerns, "Reassurances": reassurances}
```

### 4. Google Calendar Integration

``` python
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os

# Authenticate Google Calendar API
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

service = authenticate_google_calendar()

def schedule_meeting(patient_name, date, time):
    event = {
        'summary': f'Meeting with {patient_name}',
        'description': 'Follow-up meeting for mental health check-in.',
        'start': {'dateTime': f'{date}T{time}:00', 'timeZone': 'UTC'},
        'end': {'dateTime': f'{date}T{time}:30', 'timeZone': 'UTC'},
    }
    service.events().insert(calendarId='primary', body=event).execute()
```

## Installation & Setup

### 1.Install dependencies

``` bash
pip install -r requirements.txt
```

### 2. Run streamlit
```bash
streamlit run app.py
```



## Screenshots

1. ![Main Window](https://github.com/Anil970198/INFOSYS-TeleMedicine/blob/fd98c12dd2b2d8390b5ce066f1f8dd8b98444a90/images/Main%20window.png)


2. ![Streamlit App - Scheduling a Meeting](https://github.com/Anil970198/INFOSYS-TeleMedicine/blob/fd98c12dd2b2d8390b5ce066f1f8dd8b98444a90/images/Meeting%20Scheduled.png)

3. ![Google Calendar](https://github.com/Anil970198/INFOSYS-TeleMedicine/blob/fd98c12dd2b2d8390b5ce066f1f8dd8b98444a90/images/Google%20calendar.png)



## Technologies Used

- **Python, Pandas, NLTK, SpaCy** for NLP processing.
- **Streamlit** for interactive dashboard.
- **Google Calendar API** for scheduling meetings.

## Contribution

This README provides an overview of the project, including the general approach, essential code snippets, and workflow screenshots. Let me know if you'd like any refinements!

