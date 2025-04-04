import firebase_admin
from firebase_admin import credentials, firestore, storage, auth  # Added auth for authentication
import os
import requests

# Get the absolute path to google-services.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "google-services.json")

# Initialize Firebase Admin SDK (for Firestore, Storage, and Authentication)
if not firebase_admin._apps:
    cred = credentials.Certificate(CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'powerpay-android.appspot.com'
    })

db = firestore.client()
firebase_storage = storage.bucket()

# Firebase Authentication REST API
API_KEY = "AIzaSyBKlrIrq3PtyVqUplqPEmW5ZXULAJpNfIg"  # Keep this secure
FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts"

# Authentication functions using Firebase REST API
def login(email, password):
    """Log in a user with email and password using Firebase REST API"""
    try:
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(f"{FIREBASE_AUTH_URL}:signInWithPassword?key={API_KEY}", json=payload)
        data = response.json()
        
        if "error" in data:
            return data["error"]["message"]  # Firebase error message
        
        return data  # Returns the user data with ID token
    except Exception as e:
        return str(e)

def signup(email, password):
    """Sign up a new user with email and password using Firebase REST API"""
    try:
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(f"{FIREBASE_AUTH_URL}:signUp?key={API_KEY}", json=payload)
        data = response.json()
        
        if "error" in data:
            return data["error"]["message"]
        
        return data  # Returns the new user data with ID token
    except Exception as e:
        return str(e)

def fetch_user_data(user_id):
    """Fetch user data from Firestore"""
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None

def save_user_data(user_id, user_info):
    """Save user data in Firestore"""
    db.collection("users").document(user_id).set(user_info)

def upload_image(local_path, storage_path):
    """ Uploads an image to Firebase Storage and returns the download URL """
    try:
        blob = firebase_storage.blob(storage_path)
        blob.upload_from_filename(local_path)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print("⚠️ Error uploading image:", str(e))
        return None

def delete_old_image(image_url):
    """ Extracts the storage path from the Firebase Storage URL and deletes the old image. """
    try:
        if image_url:
            # Extract the file name from the URL
            storage_path = image_url.split("/")[-1]  # Get the last part of the URL (the file name)
            
            # Delete the image from Firebase Storage
            blob = firebase_storage.blob(storage_path)
            blob.delete()
            print(f"🗑️ Old image '{storage_path}' deleted successfully!")
    except Exception as e:
        print("⚠️ Error deleting old image:", str(e))
