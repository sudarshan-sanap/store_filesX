from kivy.uix.screenmanager import Screen
from google.cloud import firestore
from kivymd.app import MDApp

db = firestore.Client()

class SignupScreen(Screen):
    def register(self, email, password, first_name, last_name):
        if self.check_email_exists(email):
            self.ids.signup_message.text = "Email already exists"
            return
        app = MDApp.get_running_app()
        app.logged_in_user_email = email
        app.profile_info = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password,
        }
        self.save_to_firestore(app.profile_info)
        app.root.current = 'login'

    def check_email_exists(self, email):
        doc = db.collection('profiles').document(email).get()
        return doc.exists

    def save_to_firestore(self, profile_info):
        user_id = profile_info['email']
        db.collection('profiles').document(user_id).set(profile_info)
