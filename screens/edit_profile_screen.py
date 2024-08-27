from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from google.cloud import firestore, storage
from kivy.uix.filechooser import FileChooserIconView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "kivy-service-account-key.json"

db = firestore.Client()
storage_client = storage.Client()
bucket = storage_client.bucket("your-bucket-name")  # Replace with your Firebase Storage bucket name

class EditProfileScreen(Screen):
    dialog = None

    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        edit_screen = app.root.get_screen('edit_profile')
        edit_screen.ids.first_name.text = app.profile_info.get('first_name', '')
        edit_screen.ids.last_name.text = app.profile_info.get('last_name', '')
        edit_screen.ids.additional_name.text = app.profile_info.get('additional_name', '')
        edit_screen.ids.headline.text = app.profile_info.get('headline', '')
        edit_screen.ids.current_position.text = app.profile_info.get('current_position', '')
        edit_screen.ids.industry.text = app.profile_info.get('industry', '')
        edit_screen.ids.education.text = app.profile_info.get('education', '')
        edit_screen.ids.location.text = app.profile_info.get('location', '')
        edit_screen.ids.contact_info.text = app.profile_info.get('contact_info', '')
        edit_screen.ids.website.text = app.profile_info.get('website', '')
        profile_image_url = app.profile_info.get('profile_image', '')
        if profile_image_url:
            edit_screen.ids.profile_image.source = profile_image_url

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
            'email': app.logged_in_user_email,  # Ensure to include the email
            'profile_image': app.profile_info.get('profile_image', "")
        }
        db.collection('profiles').document(app.logged_in_user_email).set(profile_data)
        app.profile_info.update(profile_data)
        app.root.get_screen('profile').update_profile_info(profile_data)
        app.root.current = 'profile'

    def save_to_firestore(self, profile_info):
        app = MDApp.get_running_app()
        user_id = app.logged_in_user_email  # Ensure this is set during login
        db.collection('profiles').document(user_id).set(profile_info)

    def show_file_chooser(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Select Profile Image",
                type="custom",
                content_cls=FileChooserIconView(),
                buttons=[
                    MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                    MDFlatButton(text="SELECT", on_release=self.upload_profile_image),
                ],
            )
        self.dialog.open()

    def upload_profile_image(self, *args):
        filechooser = self.dialog.content_cls
        selected = filechooser.selection
        if selected:
            file_path = selected[0]
            blob = bucket.blob(f"profile_images/{os.path.basename(file_path)}")
            blob.upload_from_filename(file_path)
            app = MDApp.get_running_app()
            app.profile_info['profile_image'] = blob.public_url
            self.dialog.dismiss()
            self.save_profile_info(
                app.profile_info['first_name'],
                app.profile_info['last_name'],
                app.profile_info['additional_name'],
                app.profile_info['headline'],
                app.profile_info['current_position'],
                app.profile_info['industry'],
                app.profile_info['education'],
                app.profile_info['location'],
                app.profile_info['contact_info'],
                app.profile_info['website']
            )
