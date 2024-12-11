# TODO data_base_util Dummy

# TODO Remove this after the database is implemented
# Dummy user database
USERS = {
    "user1": {"user_id": "4eecc7ff58662618", "username": "user1", "password": "password123", "remember_me": True, "bio": "This is User 1's bio."},
    "user2": {"user_id": "d5377bb4777aa34c", "username": "user2", "password": "securepass", "remember_me": True, "bio": "Welcome to User 2's personal bio page."}
}

def find_user_by_username(username: str):
    return USERS[username]

def save_user(user_data):
    pass

def users_with_remember_me():
    return [{'username': user, **details} for user, details in USERS.items() if details["remember_me"]]

def get_user_ids():
    return [user["user_id"] for user in USERS.values()]
