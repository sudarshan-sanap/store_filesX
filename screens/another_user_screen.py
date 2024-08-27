from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from google.cloud import firestore
import os
import logging

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "kivy-service-account-key.json"

db = firestore.Client()

class AnotherUserScreen(Screen):
    name = 'another_user'  # Adding the name attribute here

    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        if not app.selected_user_info:
            logging.error("No user email provided to load another user profile.")
            return
        logging.info(f"Loading profile for user: {app.selected_user_info['email']}")
        self.load_another_user_profile(app.selected_user_info['email'])

    def load_another_user_profile(self, user_email):
        try:
            user_ref = db.collection('profiles').document(user_email)
            user_data = user_ref.get().to_dict()
            if user_data:
                logging.info(f"User profile found for: {user_email}")
                self.update_profile_info(user_data)
            else:
                logging.error(f"User profile not found for: {user_email}")
        except Exception as e:
            logging.error(f"Failed to load user profile for {user_email}: {str(e)}")

    def update_profile_info(self, profile_data):
        profile_screen = self.ids
        
        # Update the full name
        full_name = profile_data.get('first_name', '') + " " + profile_data.get('last_name', '')
        profile_screen.another_user_full_name.text = full_name if full_name.strip() else "Name not available"
        logging.debug(f"Full name set to: {full_name}")
        
        # Update the headline
        headline = profile_data.get('headline', '..') or '..'
        profile_screen.another_user_headline.text = headline
        logging.debug(f"Headline set to: {headline}")
        
        # Update the profile image
        profile_image_url = profile_data.get('profile_image', 'default_profile.png')
        profile_screen.another_user_profile_image.source = profile_image_url
        logging.debug(f"Profile image set to: {profile_image_url}")
