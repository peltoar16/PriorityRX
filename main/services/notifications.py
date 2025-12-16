import os
from dotenv import load_dotenv
load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM = os.getenv('TWILIO_FROM')

def notify_patient(patient, message):
    # For demo: print to console and optionally send via Twilio if credentials exist
    print(f"[NOTIFY] To {patient.phone or patient.email}: {message}")
    try:
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and patient.phone:
            from twilio.rest import Client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            client.messages.create(
                to=patient.phone,
                from_=TWILIO_FROM,
                body=message
            )
    except Exception as e:
        print("Failed to send SMS (demo):", e)