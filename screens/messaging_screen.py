from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivymd.app import MDApp
from google.cloud import firestore
import logging

class ChatBubble(MDBoxLayout):  # Using MDBoxLayout for consistent material design
    message = StringProperty()
    is_current_user = BooleanProperty(False)

class MessagingScreen(Screen):
    chat_user_email = None

    def on_pre_enter(self):
        logging.info("Entering MessagingScreen, preparing chat history.")
        self.clear_chat_list()
        if self.chat_user_email:
            self.load_chat_history(self.chat_user_email)

    def clear_chat_list(self):
        if 'chat_list' in self.ids:
            self.ids.chat_list.clear_widgets()
        else:
            logging.error("chat_list ID not found in screen.")

    def start_chat_with_user(self, user_data):
        logging.info(f"Starting chat with user data: {user_data}")
        if 'email' not in user_data:
            logging.error("User data does not contain 'email' key.")
            return

        self.chat_user_email = user_data['email']
        self.ids.toolbar.title = f"Chat with {user_data.get('first_name', '')} {user_data.get('last_name', '')}"
        self.ids.no_user_selected_label.opacity = 0
        self.load_chat_history(self.chat_user_email)

    def load_chat_history(self, chat_user_email):
        logging.info(f"Loading chat history with {chat_user_email}")
        if 'chat_list' not in self.ids:
            logging.error("Chat list not found in screen IDs.")
            return

        self.clear_chat_list()

        db = firestore.Client()
        current_user_email = MDApp.get_running_app().logged_in_user_email
        chats_ref = db.collection('chats').document(current_user_email).collection(chat_user_email).order_by('timestamp').stream()

        for chat in chats_ref:
            chat_data = chat.to_dict()
            logging.info(f"Loaded chat message: {chat_data}")
            chat_item = self.create_chat_item(chat_data['message'], chat_data['sender'] == current_user_email)
            if chat_item is not None:
                self.ids.chat_list.add_widget(chat_item)
            else:
                logging.error("Failed to add chat_item to chat_list because it's None.")

        # Scroll to the bottom of the chat list
        self.ids.chat_list.parent.scroll_to(self.ids.chat_list.children[-1] if self.ids.chat_list.children else self.ids.chat_list)


    def create_chat_item(self, message, is_current_user):
        chat_item = ChatBubble(message=message, is_current_user=is_current_user)
        if chat_item is None:
            logging.error("Failed to create chat item. The returned chat_item is None.")
        else:
            logging.info(f"Created chat item with message: {message}")
        return chat_item

    def send_message(self, message_text=None):
        if message_text is None:
            message_text = self.ids.message_input.text.strip()
        if message_text and self.chat_user_email:
            logging.info(f"Sending message: {message_text} to {self.chat_user_email}")
            db = firestore.Client()
            current_user_email = MDApp.get_running_app().logged_in_user_email
            chat_data = {
                'message': message_text,
                'sender': current_user_email,
                'receiver': self.chat_user_email,
                'timestamp': firestore.SERVER_TIMESTAMP
            }
            logging.info(f"Sending message data: {chat_data}")
            db.collection('chats').document(current_user_email).collection(self.chat_user_email).add(chat_data)
            db.collection('chats').document(self.chat_user_email).collection(current_user_email).add(chat_data)
            self.load_chat_history(self.chat_user_email)
            self.ids.message_input.text = ''
        else:
            logging.warning("Message text is empty or chat user email is not set.")
