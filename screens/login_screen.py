from kivy.uix.screenmanager import Screen
from google.cloud import firestore
from kivymd.app import MDApp
import logging
import os


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "kivy-service-account-key.json"

db = firestore.Client()

class LoginScreen(Screen):
    def login(self, email, password):
        app = MDApp.get_running_app()
        user_ref = db.collection('profiles').document(email)
        user_data = user_ref.get().to_dict()
        
        if user_data and 'password' in user_data and user_data['password'] == password:
            app.logged_in_user_email = email
            app.profile_info = user_data
            app.root.current = 'home'
            logging.info("Login successful")
        else:
            logging.error("Login failed: Incorrect email or password")
            self.ids.login_message.text = "Incorrect email or password"
            self.ids.login_message.color = (1, 0, 0, 1)  # Red color for error
