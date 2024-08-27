import logging
from google.cloud import firestore
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivy.uix.image import AsyncImage

from screens.login_screen import LoginScreen
from screens.signup_screen import SignupScreen
from screens.home_screen import HomeScreen
from screens.profile_screen import ProfileScreen
from screens.password_reset_screen import PasswordResetScreen
from screens.edit_profile_screen import EditProfileScreen
from screens.messaging_screen import MessagingScreen
from screens.another_user_screen import AnotherUserScreen
from screens.post_feed_screen import PostFeedScreen
from kivy.uix.boxlayout import BoxLayout

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "kivy-service-account-key.json"
db = firestore.Client()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class WindowManager(ScreenManager):
    pass

class Sidebar(BoxLayout):
    pass

class MainApp(MDApp):
    profile_info = {}
    logged_in_user_email = ""
    viewing_own_profile = False
    chat_user_email = ""

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        # Load each kv file separately
        Builder.load_file('kv/login.kv')
        Builder.load_file('kv/signup.kv')
        Builder.load_file('kv/home.kv')
        Builder.load_file('kv/profile.kv')
        Builder.load_file('kv/password_reset.kv')
        Builder.load_file('kv/edit_profile.kv')
        Builder.load_file('kv/messaging.kv')
        Builder.load_file('kv/another_user.kv')
        Builder.load_file('kv/post_feed.kv')
        Builder.load_file('kv/sidebar.kv')
        return Builder.load_file('main.kv')

    def open_nav_drawer(self):
        self.root.get_screen('home').ids.nav_drawer.set_state('open')

    def view_profile(self, user_email=None):
        if user_email and user_email != self.logged_in_user_email:
            # Viewing another user's profile
            self.selected_user_info = self.get_user_profile(user_email)
            if self.selected_user_info:
                logging.debug(f"Available Screens: {[screen.name for screen in self.root.screens]}")
                self.root.current = 'another_user'
                self.root.get_screen('another_user').update_profile_info(self.selected_user_info)
                logging.info(f"Viewing profile of another user: {user_email}")
        else:
            # Viewing logged-in user's profile
            self.root.current = 'profile'
            self.root.get_screen('profile').update_profile_info(self.profile_info)
            logging.info("Viewing own profile")

    def edit_intro(self):
        self.root.current = 'edit_profile'
        logging.info("Navigated to Edit Profile")

    def back_to_home(self):
        self.root.current = 'home'
        logging.info("Navigated back to Home")

    def sign_out(self):
        logging.debug("Signing out user.")
        # Clear the logged-in user data
        self.logged_in_user_email = ""
        self.profile_info = {}
        self.viewing_own_profile = False

        # Redirect to the home screen first
        self.back_to_home()
        
        # Clear UI elements that may retain previous user data
        home_screen = self.root.get_screen('home')
        
        if 'search_results_list' in home_screen.ids:
            home_screen.ids.search_results_list.clear_widgets()
        
        if 'feed_rv' in home_screen.ids:
            home_screen.ids.feed_rv.data = []
        
        # Only clear post_content if it exists
        if 'post_content' in home_screen.ids:
            home_screen.ids.post_content.text = ''
        
        # Reset the profile screen UI elements
        profile_screen = self.root.get_screen('profile')
        profile_screen.ids.full_name.text = ""
        profile_screen.ids.headline.text = ""
        profile_screen.ids.industry.text = ""
        profile_screen.ids.location.text = ""
        profile_screen.ids.contact_info.text = ""
        profile_screen.ids.website.text = ""
        
        # Redirect to the login screen
        self.root.current = 'login'

    def perform_search(self, query):
        logging.info(f"Searching for users with query: {query}")
        db = firestore.Client()
        users_ref = db.collection('profiles')
        user_query = users_ref.where('first_name', '>=', query).where('first_name', '<=', query + '\uf8ff').stream()

        search_results = []
        for doc in user_query:
            user_data = doc.to_dict()
            if 'email' not in user_data:
                logging.error(f"Found user without email key: {user_data}")
            else:
                search_results.append(user_data)
                logging.info(f"Found user: {user_data}")

        self.update_search_results_list(search_results)

    def update_search_results(self, text):
        logging.debug(f"Search text changed: {text}")
        if text.strip() == "":
            self.root.get_screen('home').ids.search_results_list.clear_widgets()
            return
        self.perform_search(text)

    def update_search_results_list(self, search_results):
        logging.info(f"Updating search results list with {len(search_results)} results.")
        search_results_list = self.root.get_screen('home').ids.search_results_list
        search_results_list.clear_widgets()
        for result in search_results:
            item = OneLineListItem(text=result.get('first_name', '') + " " + result.get('last_name', ''))
            item.bind(on_release=lambda x, user_data=result: self.open_user_profile(user_data))
            search_results_list.add_widget(item)
        logging.info("Search results list updated.")

    def open_user_profile(self, user_data):
        logging.info(f"Opening profile for user: {user_data}")
        if 'email' not in user_data:
            logging.error("User data does not contain 'email' key.")
            return
        
        # Separate handling for logged-in user and another user's profile
        if self.logged_in_user_email == user_data.get('email'):
            # Viewing own profile
            self.profile_info = user_data  # This ensures that the logged-in user's data remains correct
            self.viewing_own_profile = True
            self.root.current = 'profile'
            self.root.get_screen('profile').update_profile_info(self.profile_info)
            logging.info(f"Opened logged-in user's profile: {user_data}")
        else:
            # Viewing another user's profile
            self.selected_user_info = user_data  # Store the selected user's data separately
            self.viewing_own_profile = False
            self.root.current = 'another_user'
            self.root.get_screen('another_user').update_profile_info(self.selected_user_info)
            logging.info(f"Opened profile of another user: {user_data}")

    def open_messaging_page(self):
        if 'email' not in self.selected_user_info:
            logging.error("Selected user info does not contain 'email' key.")
            return
        logging.info(f"Opening messaging page for {self.selected_user_info['email']}")
        self.root.get_screen('messaging').start_chat_with_user(self.selected_user_info)
        self.root.current = 'messaging'

    def open_post_page(self):
        self.root.current = 'post_feed'  # Assuming you have a screen named 'post_feed' for adding posts

    def get_profile_toolbar_items(self):
        items = []
        if self.viewing_own_profile:
            items.append(["pencil", lambda x: self.edit_intro()])
        return items

if __name__ == '__main__':
    MainApp().run()
