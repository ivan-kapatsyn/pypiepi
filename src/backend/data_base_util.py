# TODO data_base_util Dummy

# TODO Remove this after the database is implemented
# Dummy user database
# user1 password: password123, user2: securepass
USERS = {
    "4eecc7ff58662618": {"user_id": "4eecc7ff58662618", "username": "user1", "password": "JDJiJDEyJFVjY0hnYWRZZzk5QlM3cEduUnkwRnV3QTh0VVRmN2p4RHdNTklIYkZZOG01dTRmWDhNd2ku", "remember_me": True, "bio": "This is User 1's bio."},
    "d5377bb4777aa34c": {"user_id": "d5377bb4777aa34c", "username": "user2", "password": "JDJiJDEyJFdjOVlPRHMuTzVjRkJkOUFlMUVEVHUyMm5IRVVRUEZScjJwNFh6UFRpME1QWnA2clU3Nmtt", "remember_me": True, "bio": "Welcome to User 2's personal bio page."}
}

def find_user_by_username(username: str):
    for user in USERS.values():
        if user["username"] == username:
            return user
    return {}

def find_user_by_id(user_id: str):
    return USERS.get(user_id, {})

def save_user(user_data):
    pass

def users_with_remember_me():
    return [details for details in USERS.values() if details["remember_me"]]

def get_user_ids():
    return [user["user_id"] for user in USERS.values()]
