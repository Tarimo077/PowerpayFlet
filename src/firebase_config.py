import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
import os

# Get the absolute path to google-services.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "google-services.json")

# Initialize Firebase Admin SDK (for Firestore)
cred = credentials.Certificate(CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Firebase Authentication Config (for Pyrebase)
firebaseConfig = {
    "apiKey": "AIzaSyBKlrIrq3PtyVqUplqPEmW5ZXULAJpNfIg",
    "authDomain": "powerpay-android.firebaseapp.com",
    "databaseURL": "",  # Add if you use Firebase Realtime Database
    "projectId": "powerpay-android",
    "storageBucket": "powerpay-android.appspot.com",
    "messagingSenderId": "915158642951",
    "appId": "1:915158642951:android:51756e78d90e56303195a2"
}

# Initialize Pyrebase (for Authentication)
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        return str(e)

def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user
    except Exception as e:
        return str(e)

def fetch_user_data(user_id):
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None

def save_user_data(user_id, user_info):
    db.collection("users").document(user_id).set(user_info)
