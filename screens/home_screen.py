from kivy.uix.screenmanager import Screen
from google.cloud import firestore
import os
import logging
import datetime
from pytz import timezone
from kivy.logger import Logger
from kivymd.app import MDApp
Logger.setLevel('DEBUG')


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "kivy-service-account-key.json"

db = firestore.Client()

class HomeScreen(Screen):

    def on_pre_enter(self, *args):
        logging.info("Entering HomeScreen, loading posts.")
        self.load_posts()

    def on_leave(self):
        # Clean up any references or UI components safely
        if 'post_content' in self.ids:
            self.ids.post_content.text = ''

    def load_posts(self):
        logging.info("Loading posts for feed.")
        db = firestore.Client()
        posts_ref = db.collection('posts').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()

        feed = []
        for post in posts_ref:
            post_data = post.to_dict()
            post_id = post.id  # Get the ID of the post

            # Convert the Firestore timestamp to the local timezone
            timestamp = post_data.get('timestamp')
            if timestamp:
                timestamp = timestamp.replace(tzinfo=datetime.timezone.utc).astimezone(timezone('Asia/Kolkata')).strftime('%I:%M %p')
            else:
                timestamp = ''

            # Check if the current user has liked the post
            liked_by_user = MDApp.get_running_app().logged_in_user_email in post_data.get('likes', [])

            feed_item = {
                'post_id': post_id,
                'user': post_data.get('user', 'Anonymous'),
                'timestamp': timestamp,
                'content': post_data.get('content', ''),
                'image': post_data.get('image', ''),
                'likes_count': str(len(post_data.get('likes', []))),
                'liked_by_user': liked_by_user
            }
            feed.append(feed_item)

        self.ids.feed_rv.data = feed
        logging.info(f"Loaded {len(feed)} posts.")

    def on_like_pressed(self, post_id):
        logging.info(f"Like button pressed for post: {post_id}")
        user_email = MDApp.get_running_app().logged_in_user_email
        post_ref = db.collection('posts').document(post_id)
        post = post_ref.get()
        post_data = post.to_dict()

        # Ensure 'likes' is initialized as an empty list if not present
        if 'likes' not in post_data:
            post_data['likes'] = []

        if user_email in post_data['likes']:
            # Unlike the post
            post_data['likes'].remove(user_email)
            liked = False
        else:
            # Like the post
            post_data['likes'].append(user_email)
            liked = True

        post_ref.update({'likes': post_data['likes']})
        self.load_posts()  # Reload posts to reflect changes
        logging.info(f"Post {post_id} {'liked' if liked else 'unliked'} by {user_email}")

