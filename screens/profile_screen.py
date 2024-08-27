from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from google.cloud import firestore
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "kivy-service-account-key.json"

db = firestore.Client()

class ProfileScreen(Screen):
    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        self.update_profile_info(app.profile_info)

    def update_profile_info(self, profile_data):
        app = MDApp.get_running_app()
        profile_screen = app.root.get_screen('profile')
        profile_screen.ids.toolbar.title = "View Profile"

        # Conditionally show the edit icon
        if app.viewing_own_profile:
            profile_screen.ids.toolbar.right_action_items = [['pencil', lambda x: app.edit_intro()]]
        else:
            profile_screen.ids.toolbar.right_action_items = []

        # Update all the labels
        profile_screen.ids.full_name.text = profile_data.get('first_name', '') + " " + profile_data.get('last_name', '')
        profile_screen.ids.headline.text = profile_data.get('headline', '..') or '..'
        profile_screen.ids.industry.text = profile_data.get('industry', '')
        profile_screen.ids.location.text = profile_data.get('location', '')

    def save_profile_info(self, first_name, last_name, additional_name, headline, current_position, industry, education, location, contact_info, website):
        app = MDApp.get_running_app()
        profile_data = {
            'first_name': first_name,
            'last_name': last_name,
            'additional_name': additional_name,
            'headline': headline,
            'current_position': current_position,
            'industry': industry,
            'education': education,
            'location': location,
            'contact_info': contact_info,
            'website': website,
            'email': app.logged_in_user_email  # Ensure to include the email
        }
        db.collection('profiles').document(app.logged_in_user_email).set(profile_data)
        app.profile_info.update(profile_data)
        app.root.get_screen('profile').update_profile_info(profile_data)
        app.root.current = 'profile'

    def save_to_firestore(self, profile_info):
        user_id = profile_info['email']
        db.collection('profiles').document(user_id).set(profile_info)
