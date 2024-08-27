from kivy.uix.screenmanager import Screen
from google.cloud import firestore
from kivymd.app import MDApp

db = firestore.Client()

class PasswordResetScreen(Screen):
    def reset_password(self, email, new_password):
        if not email or not new_password:
            self.ids.reset_message.text = "Please enter your email and new password"
            self.ids.reset_message.color = (1, 0, 0, 1)  # Red color for error
            return
        
        if len(new_password) < 8 or len(new_password) > 16:
            self.ids.reset_message.text = "Please enter password character between 8 and 16"
            self.ids.reset_message.color = (1, 0, 0, 1)  # Red color for error
            return

        user_doc = db.collection('profiles').document(email).get()
        if user_doc.exists:
            # Update the user's password
            db.collection('profiles').document(email).update({'password': new_password})
            self.ids.reset_message.text = "Password has been reset successfully"
            self.ids.reset_message.color = (0, 1, 0, 1)  # Green color for success
        else:
            self.ids.reset_message.text = "Email not found"
            self.ids.reset_message.color = (1, 0, 0, 1)  # Red color for error

    def back_to_login(self):
        self.ids.email.text = ""
        self.ids.new_password.text = ""
        self.ids.reset_message.text = ""
        self.manager.current = 'login'
