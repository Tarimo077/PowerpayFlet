import firebase_admin
from firebase_admin import credentials, firestore, storage
import pyrebase
import os
import urllib.parse

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
# Initialize Firebase Admin SDK (for Firestore and Storage)
#if not firebase_admin._apps:
#    cred = credentials.Certificate(CREDENTIALS_PATH)
#    firebase_admin.initialize_app(cred, {
#        'storageBucket': 'powerpay-android.appspot.com'  # Make sure this is correct
#    })
auth = firebase.auth()
# Firebase Storage client
firebase_storage = storage.bucket(name="powerpay-android.appspot.com")



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

def upload_image(local_path, storage_path):
    """ Uploads an image to Firebase Storage and returns the download URL """
    try:
        blob = firebase_storage.blob(storage_path)

        # Upload file
        blob.upload_from_filename(local_path)

        # Generate a public URL
        blob.make_public()

        return blob.public_url
    except Exception as e:
        print("⚠️ Error uploading image:", str(e))
        return None

    
def delete_old_image(image_url):
    """ Extracts the storage path from the Firebase Storage URL and deletes the old image. """
    try:
        if "firebasestorage.googleapis.com" in image_url:
            # Extract the encoded file path
            encoded_path = image_url.split("/o/")[-1].split("?alt=media")[0]

            # Decode the URL-encoded path (Firebase encodes `/` as `%2F`)
            storage_path = urllib.parse.unquote(encoded_path)

            # Delete the image using Firebase Admin SDK
            blob = firebase_storage.blob(storage_path)
            blob.delete()

            print("🗑️ Old image deleted successfully!")
    except Exception as e:
        print("⚠️ Error deleting old image:", str(e))

