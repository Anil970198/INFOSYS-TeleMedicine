import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import base64
from io import BytesIO
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os

# Load data
with open('C:/Users/srira/OneDrive/Desktop/docpat/data.pkl', 'rb') as file:
    data = pickle.load(file)

symptom_categories = {
    'Common': ['Fever', 'Cough', 'Fatigue', 'Headache', 'Pain'],
    'Respiratory': ['Dyspnea', 'Shortness of breath'],
    'Gastrointestinal': ['Nausea', 'Vomiting', 'Diarrhea', 'Loss of appetite'],
    'Neurological': ['Dizziness', 'Seizure', 'Numbness', 'Tingling'],
    'Other': ['Bleeding', 'Chills', 'Rash', 'Sweating', 'Swelling', 'Weakness', 'Stress']
}

symptoms = [symptom for category in symptom_categories.values() for symptom in category]

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'C:/Users/srira/OneDrive/Desktop/docpat/client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

service = authenticate_google_calendar()

def generate_wordcloud(text):
    wc = WordCloud(background_color='white', width=800, height=400, colormap='viridis', max_words=100).generate(' '.join(text))
    img = BytesIO()
    wc.to_image().save(img, format='PNG')
    img.seek(0)
    return base64.b64encode(img.read()).decode('utf-8')

# Prepare data
symptom_counts = data['symptoms'].explode().value_counts().reset_index()
symptom_counts.columns = ['Symptom', 'Count']

disease_counts = data['diseases'].explode().value_counts().reset_index()
disease_counts.columns = ['Disease', 'Count']

gender_counts = data['gender'].value_counts().reset_index()
gender_counts.columns = ['Gender', 'Count']

age_distribution = data['age'].dropna()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server

# Layout remains the same until the risk table part
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4("Clinical Analytics", className="text-primary mb-4"),
                html.H5("Risk Assessment", className="mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        html.Label("Filter by Symptoms", className="mb-2"),
                        dcc.Dropdown(
                            id='symptom-category',
                            options=[{'label': category, 'value': category} for category in symptom_categories.keys()],
                            placeholder="Select Category",
                            className="mb-3"
                        ),
                        dcc.Dropdown(
                            id='high-risk-filter',
                            multi=True,
                            placeholder="Select Symptoms",
                            className="mb-3"
                        ),
                        dcc.DatePickerSingle(
                            id='meeting-date',
                            date=None,
                            display_format='YYYY-MM-DD',
                            className="mb-3"
                        ),
                        dbc.Button(
                            "Schedule Meeting",
                            id='schedule-button',
                            color="primary",
                            className="w-100",
                            n_clicks=0
                        )
                    ])
                ]),
                html.Div(id='high-risk-output', className="mt-3"),
                html.Div(id='schedule-output', className="mt-3")
            ], className="sticky-top")
        ], width=3, className="bg-light p-4"),

        dbc.Col([
            html.H2("Clinical Data Analytics Dashboard", className="text-center mb-4"),
            
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H3(len(data), className="text-center text-primary"),
                        html.P("Total Conversations", className="text-center text-muted")
                    ])
                ]), width=4),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H3(len(set([item for sublist in data['symptoms'] for item in sublist])),
                               className="text-center text-success"),
                        html.P("Unique Symptoms", className="text-center text-muted")
                    ])
                ]), width=4),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H3(len(set([item for sublist in data['diseases'] for item in sublist])),
                               className="text-center text-info"),
                        html.P("Unique Diseases", className="text-center text-muted")
                    ])
                ]), width=4),
            ], className="mb-4"),

            dbc.Tabs([
                dbc.Tab([
                    dbc.Row([
                        dbc.Col(dcc.Graph(
                            id='symptom-treemap',
                            figure=px.treemap(symptom_counts, path=['Symptom'], values='Count', title="Symptom Distribution")
                        ), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Symptom Word Cloud", className="text-center"),
                            html.Img(
                                src=f"data:image/png;base64,{generate_wordcloud([item for sublist in data['symptoms'] for item in sublist])}",
                                className="img-fluid"
                            )
                        ], width=12)
                    ])
                ], label="Symptoms Analysis"),
                
                dbc.Tab([
                    dbc.Row([
                        dbc.Col(dcc.Graph(
                            id='disease-sunburst',
                            figure=px.sunburst(disease_counts, path=['Disease'], values='Count', title="Disease Distribution")
                        ), width=12)
                    ])
                ], label="Disease Analysis"),
                
                dbc.Tab([
                    dbc.Row([
                        dbc.Col(dcc.Graph(
                            id='demographics-scatter',
                            figure=px.scatter(data, x='age', y='gender', color='gender', title="Patient Demographics")
                        ), width=6),
                        dbc.Col(dcc.Graph(
                            id='age-violin',
                            figure=px.violin(data, y='age', box=True, points="all", title="Age Distribution")
                        ), width=6)
                    ])
                ], label="Demographics")
            ])
        ], width=9, className="p-4")
    ])
], fluid=True)

@app.callback(
    Output('high-risk-filter', 'options'),
    [Input('symptom-category', 'value')]
)
def update_symptom_options(category):
    if category:
        return [{'label': symptom, 'value': symptom} for symptom in symptom_categories[category]]
    return []

@app.callback(
    [Output('high-risk-output', 'children'),
     Output('schedule-output', 'children')],
    [Input('schedule-button', 'n_clicks')],
    [State('high-risk-filter', 'value'),
     State('meeting-date', 'date')]
)
def update_risk_assessment(n_clicks, selected_symptoms, meeting_date):
    if n_clicks is None:
        return None, None
    
    if not selected_symptoms:
        return html.P("Select symptoms to identify high-risk patients.", className="text-muted"), None
    
    filtered = data[data['symptoms'].apply(lambda x: all(symptom in x for symptom in selected_symptoms))]
    
    if filtered.empty:
        return html.P("No patients found matching the criteria.", className="text-warning"), None
    
    # Updated risk table with dbc.Badge instead of html.Badge
    risk_table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("ID"),
            html.Th("Summary"),
            html.Th("Risk Level")
        ])),
        html.Tbody([
            html.Tr([
                html.Td(row['serial_number']),
                html.Td(row['data'][:100] + "..."),
                html.Td(dbc.Badge("High Risk", color="danger", className="ms-1"))
            ]) for _, row in filtered.iterrows()
        ])
    ], bordered=True, hover=True, responsive=True)
    
    if n_clicks > 0 and meeting_date:
        try:
            for _, row in filtered.iterrows():
                event = {
                    'summary': f"High Risk Patient {row['serial_number']} Consultation",
                    'description': f"Patient Data: {row['data']}",
                    'start': {'dateTime': f'{meeting_date}T10:00:00', 'timeZone': 'America/New_York'},
                    'end': {'dateTime': f'{meeting_date}T10:30:00', 'timeZone': 'America/New_York'}
                }
                service.events().insert(calendarId='primary', body=event).execute()
            return risk_table, dbc.Alert("Meetings scheduled successfully!", color="success")
        except Exception as e:
            return risk_table, dbc.Alert(f"Error scheduling meetings: {str(e)}", color="danger")
    
    return risk_table, None

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)