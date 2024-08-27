import kivy
from kivy.uix.screenmanager import Screen
from google.cloud import firestore, storage
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.utils import platform
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import os
import logging

db = firestore.Client()
storage_client = storage.Client()

def upload_image_to_storage(image_path, cloud_path):
    try:
        bucket = storage_client.bucket('connectin-posts-storage')  # Ensure this bucket exists
        blob = bucket.blob(cloud_path)
        blob.upload_from_filename(image_path)
        
        # Return the public URL for the uploaded file
        base_url = "https://storage.googleapis.com"
        return f"{base_url}/{bucket.name}/{cloud_path}"
    except Exception as e:
        logging.error(f"Failed to upload image: {e}")
        return None  # Return None or raise an exception as appropriate

class PostFeedScreen(Screen):
    dialog = None
    image_url = ""

    def share_post(self, content, image_source):
        if not content.strip() and not image_source:
            self.show_blank_post_warning()
            return
        
        post_data = {
            'content': content,
            'user': MDApp.get_running_app().profile_info.get('email', 'Anonymous'),
            'timestamp': firestore.SERVER_TIMESTAMP,
            'image': image_source if image_source else '',
            'likes': []  # Ensure likes is initialized as an empty list
        }
        
        db.collection('posts').add(post_data)
        
        # Clear the input fields
        self.clear_post_fields()
        
        MDApp.get_running_app().root.current = 'home'
        MDApp.get_running_app().load_posts()

    def show_blank_post_warning(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Cannot send blank. Please share your thoughts.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.open()

    def create_post(self, text_content, image_path):
        if not text_content.strip() and not image_path:
            self.show_blank_post_warning()
            return

        post_data = {}

        if text_content:
            post_data['content'] = text_content
            
        if image_path:
            cloud_path = f"images/{os.path.basename(image_path)}"
            image_url = upload_image_to_storage(image_path, cloud_path)
            if image_url:
                post_data['image'] = image_url
            else:
                logging.warning("Image upload failed, post will not include image.")
            
        post_data['user'] = MDApp.get_running_app().logged_in_user_email
        post_data['timestamp'] = firestore.SERVER_TIMESTAMP

        db.collection('posts').add(post_data)

        self.clear_post_fields()
        MDApp.get_running_app().back_to_home()

    def clear_post_fields(self):
        self.ids.post_content.text = ''
        self.ids.selected_image.source = ''
        self.ids.selected_image.opacity = 0
        
    def load_image(self, url):
        try:
            self.ids.selected_image.source = url
        except Exception as e:
            logging.error(f"Failed to load image: {e}")
            self.ids.selected_image.source = 'path_to_placeholder_image.png'
    def open_file_chooser(self):
        platform = kivy.utils.platform
        logging.info(f"Platform detected: {platform}")
        
        if platform == 'android':
            from android.storage import primary_external_storage_path
            storage_path = primary_external_storage_path()

            from jnius import autoclass
            FileChooser = autoclass('org.renpy.android.FileChooserActivity')
            FileChooser(storage_path)
            
        elif platform == 'ios':
            from os.path import expanduser
            storage_path = expanduser("~/Documents/")
            self.show_kivy_filechooser(storage_path)
            
        else:
            storage_path = os.getcwd()
            self.show_kivy_filechooser(storage_path)

    def show_kivy_filechooser(self, initial_path):
        filechooser = FileChooserListView(path=initial_path, filters=['*.png', '*.jpg', '*.jpeg', '*.mp4'])

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(filechooser)

        select_button = Button(text="Select", size_hint_y=None, height='48dp')
        layout.add_widget(select_button)

        def on_select(instance):
            selected = filechooser.selection
            if selected:
                selected_path = selected[0]
                self.ids.selected_image.source = selected_path
                self.ids.selected_image.opacity = 1  # Make the image visible
                popup.dismiss()

        select_button.bind(on_release=on_select)

        popup = Popup(title="Choose a File", content=layout, size_hint=(0.9, 0.9))
        popup.open()

    def handle_file_selection(self, selection):
        if selection:
            self.ids.selected_image.source = selection[0]
            self.ids.selected_image.opacity = 1  # Make the image visible
