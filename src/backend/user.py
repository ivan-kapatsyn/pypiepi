# TODO Remove this after the database is implemented
# Dummy user database
USERS = {
    "user1": {"password": "password123", "bio": "This is User 1's bio."},
    "user2": {"password": "securepass", "bio": "Welcome to User 2's personal bio page."}
}

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def authenticate(self, user_db):
        user = user_db.get(self.username)
        if user and user['password'] == self.password:
            return True
        return False
