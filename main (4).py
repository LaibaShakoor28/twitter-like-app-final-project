import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime

class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.following = []
        self.tweets = []
        self.likes = []
        self.dislikes = []
        self.selected_tweet_owner = self.username

    def follow(self, other_user):
        if other_user not in self.following:
            self.following.append(other_user)
            print(f"{self.username} is now following {other_user.username}")
            self.save_to_file()

    def like_tweet(self, tweet):
        tweet["likes"] += 1
        self.save_to_file()
        print(f"{self.username} liked a tweet.")

    def post_tweet(self, content):
        self.selected_tweet_owner = None
        tweet = {
            "content": content,
            "timestamp": str(datetime.now()),
            "likes": 0,
            "dislikes": 0
        }
        self.tweets.append(tweet)
        print(f"{self.username} posted a tweet: {content}")

    def display_tweets(self):
        print(f"Tweets by {self.username}:")
        for tweet in self.tweets:
            print(f"{tweet['timestamp']} - {tweet['content']}")

    def save_to_file(self):
        user_data = {
            "username": self.username,
            "email": self.email,
            "likes": self.likes,
            "dislikes": self.dislikes,
            "following": [user.username for user in self.following],
            "tweets": self.tweets
        }
        with open(f"{self.username}_data.txt", 'w') as file:
            json.dump(user_data, file)

        # Update the global user data file with the current username
        try:
            with open("user_data.txt", 'r') as user_data_file:
                user_data = json.load(user_data_file)
                if self.username not in user_data["usernames"]:
                    user_data["usernames"].append(self.username)
        except FileNotFoundError:
            user_data = {"usernames": [self.username]}

        with open("user_data.txt", 'w') as user_data_file:
            json.dump(user_data, user_data_file)

    @classmethod
    def load_from_file(cls, username):
        try:
            with open(f"{username}_data.txt", 'r') as file:
                user_data = json.load(file)

            user = cls(user_data['username'], user_data['email'])
            user.following = [User.load_from_file(followed_user) for followed_user in user_data['following']]
            user.tweets = user_data['tweets']

            for tweet in user.tweets:
                # Handle the case where 'likes' and 'dislikes' are lists instead of integers
                tweet['likes'] = 0 if isinstance(tweet['likes'], list) else tweet['likes']
                tweet['dislikes'] = 0 if isinstance(tweet['dislikes'], list) else tweet['dislikes']

            return user
        except FileNotFoundError:
            return None


class SignupGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("User Signup")
        self.geometry("300x200")
        self.configure(bg="blue")  # Set the background color

        # Widgets
        self.label_username = tk.Label(self, text="Username:", bg="blue", fg="white")

        # Use StringVar to store and retrieve the value
        self.username_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.entry_username = tk.Entry(self, textvariable=self.username_var)

        self.label_email = tk.Label(self, text="Email:", bg="blue", fg="white")
        self.entry_email = tk.Entry(self, textvariable=self.email_var)

        self.btn_signup = tk.Button(self, text="Sign Up", command=self.signup, bg="white", fg="blue")
        self.btn_login = tk.Button(self, text="Login", command=self.login, bg="white", fg="blue")

        # Layout
        self.label_username.pack(pady=5)
        self.entry_username.pack(pady=5)
        self.label_email.pack(pady=5)
        self.entry_email.pack(pady=5)
        self.btn_signup.pack(pady=5)
        self.btn_login.pack(pady=5)

    def signup(self):
        username = self.username_var.get()
        email = self.entry_email.get()

        if username and email:
            user = User(username, email)
            user.selected_tweet_owner = None
            user.save_to_file()
            messagebox.showinfo("Signup Successful", f"User {username} signed up successfully!")
        else:
            messagebox.showwarning("Input Error", "Please enter both username and email.")

    def login(self):
        username = self.username_var.get()
        email = self.email_var.get()
        if username:
            loaded_user = User.load_from_file(username)
            if loaded_user:
                if loaded_user.username == username and loaded_user.email == email:
                    messagebox.showinfo("Login Successful", f"Welcome back, {loaded_user.username}!")
                    self.destroy()

                    # Create the main app window
                    # Composition: Using an instance of MainApp in SignupGUI
                    main_app = MainApp(loaded_user)
                    main_app.mainloop()
                else:
                    messagebox.showwarning("Login Failed", "User not found. Please sign up.")
        else:
            messagebox.showwarning("Input Error", "Please enter a username.")


class MainApp(tk.Tk):
    def __init__(self, current_user):
        super().__init__()

        self.title("Social Media Platform")
        self.geometry("600x600")

        self.current_user = current_user # Composition: MainApp contains an instance of User
        '''In the MainApp class constructor (__init__ method), an instance of the User class (current_user) is passed as a 
        parameter. This current_user instance represents the user who is currently logged in. 
        The MainApp class then uses this instance to interact with the user's data, display information, and 
        perform actions related to the user.
        This composition allows the MainApp class to leverage the functionality of the User class without directly inheriting 
        from it. The MainApp class encapsulates the user-related features within its own structure, creating a clear and modular 
        design.'''
        # Widgets
        self.label_welcome = tk.Label(self, text=f"Welcome, {self.current_user.username}!", font=("Helvetica", 16))
        self.label_welcome.pack(pady=10)

        self.listbox_tweets = tk.Listbox(self, selectmode=tk.SINGLE, height=15, width=50)
        self.listbox_tweets.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.scrollbar_tweets = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox_tweets.yview)
        self.listbox_tweets.config(yscrollcommand=self.scrollbar_tweets.set)
        self.scrollbar_tweets.pack(side=tk.RIGHT, fill=tk.Y)

        self.entry_new_tweet = tk.Entry(self, width=50)
        self.entry_new_tweet.pack(pady=5)

        self.btn_post_tweet = tk.Button(self, text="Post Tweet", command=self.post_tweet)
        self.btn_post_tweet.pack(pady=5)

        self.btn_follow_user = tk.Button(self, text="Follow", command=self.follow)
        self.btn_follow_user.pack(pady=5)

        self.btn_like_tweet = tk.Button(self, text="Like Tweet", command=self.like_tweet)
        self.btn_like_tweet.pack(pady=5)

        self.btn_dislike_tweet = tk.Button(self, text="Dislike Tweet", command=self.dislike_tweet)
        self.btn_dislike_tweet.pack(pady=5)

        self.btn_logout = tk.Button(self, text="Logout", command=self.logout)
        self.btn_logout.pack(pady=10)

        # Populate the listbox with tweets
        #self.populate_tweets()
        self.populate_all_tweets()

    def get_user_instance(self, username):
        return User.load_from_file(username)

    def populate_tweets(self):
        for user in self.current_user.following + [self.current_user]:
            for tweet in user.tweets:
                self.listbox_tweets.insert(tk.END, f"{user.username} - {tweet['content']} (Likes: {tweet['likes']}, Dislikes: {tweet['dislikes']})\n\n")

    def populate_all_tweets(self):
        # Load data for all users
        all_users = []
        with open("user_data.txt", 'r') as user_data_file:
            user_data = json.load(user_data_file)
            for username in user_data["usernames"]:
                user = User.load_from_file(username)
                if user:
                    all_users.append(user)

        # Display tweets from all users
        for user in all_users:
            for tweet in user.tweets:
                self.listbox_tweets.insert(tk.END, f"{user.username} - {tweet['content']} (Likes: {tweet['likes']}, Dislikes: {tweet['dislikes']})\n\n")

    def post_tweet(self):
        new_tweet_content = self.entry_new_tweet.get()
        if new_tweet_content:
            self.current_user.post_tweet(new_tweet_content)
            self.current_user.save_to_file()  # Save the user data to file after posting a tweet
            self.listbox_tweets.insert(tk.END, f"{self.current_user.username} - {new_tweet_content} (Likes: 0, Dislikes: 0)\n\n")
        else:
            messagebox.showwarning("Input Error", "Please enter tweet content.")

    def like_tweet(self):
        selected_tweet_index = self.listbox_tweets.curselection()
        if selected_tweet_index:
            selected_tweet_index = selected_tweet_index[0]
            selected_tweet = self.listbox_tweets.get(selected_tweet_index)
            selected_tweet_user = selected_tweet.split(" - ")[0]

            loaded_user = self.get_user_instance(selected_tweet_user)

            for user in loaded_user.following + [loaded_user]:
                for tweet in user.tweets:
                    if "likes" in tweet and "dislikes" in tweet:
                        if tweet["likes"] == 0 and tweet["dislikes"] > 0:
                            tweet["dislikes"] -= 1
                        else:
                            tweet["likes"] += 1

                        user.save_to_file()
                        messagebox.showinfo("Liked", "You liked a tweet.")
                        self.refresh_tweets()  # Refresh the tweets after liking
        else:
            messagebox.showwarning("Input Error", "Please select a tweet to like.")

    def refresh_tweets(self):
        self.listbox_tweets.delete(0, tk.END)
        self.populate_all_tweets()

    def dislike_tweet(self):
        selected_tweet_index = self.listbox_tweets.curselection()
        if selected_tweet_index:
            selected_tweet_index = selected_tweet_index[0]
            selected_tweet = self.listbox_tweets.get(selected_tweet_index)
            tweet_owner_username = selected_tweet.split(" - ")[0]
            tweet_content = selected_tweet.split(" - ")[1]
            tweet_content = tweet_content.split('(')[0].strip()

            selected_user = self.get_user_instance(tweet_owner_username)

            if selected_user:
                for tweet in selected_user.tweets:
                    if tweet["content"].strip() == tweet_content.strip():
                        if tweet["likes"] > 0:
                            tweet["likes"] -= 1
                        else:
                            tweet["dislikes"] += 1

                        selected_user.save_to_file()
                        messagebox.showinfo("Disliked", "You disliked a tweet.")
                        self.refresh_tweets()  # Refresh the tweets after disliking
        else:
            messagebox.showwarning("Input Error", "Please select a tweet to dislike.")

    def follow(self):
        selected_tweet_index = self.listbox_tweets.curselection()
        if selected_tweet_index:
            selected_tweet_index = selected_tweet_index[0]
            selected_tweet = self.listbox_tweets.get(selected_tweet_index)
            selected_tweet_user = selected_tweet.split(" - ")[0]

            loaded_user = self.get_user_instance(selected_tweet_user)

            if loaded_user:
                self.current_user.follow(loaded_user)
                messagebox.showinfo("Followed", f"You are now following {loaded_user.username}.")
                self.refresh_tweets()  # Refresh the tweets after following
        else:
            messagebox.showwarning("Input Error", "Please select a tweet to follow.")

    def logout(self):
        self.destroy()
        signup_app = SignupGUI()
        signup_app.mainloop()

if __name__ == "__main__":
    signup_app = SignupGUI()
    signup_app.mainloop()
