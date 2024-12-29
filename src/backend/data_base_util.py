# TODO data_base_util Dummy

# TODO Remove this after the database is implemented
# Dummy user database
# user1 password: password123, user2: securepass, user3: hello, user4: qwerty
USERS = {
    "4eecc7ff58662618": {"userID": "4eecc7ff58662618", "username": "user1", "password": "JDJiJDEyJFVjY0hnYWRZZzk5QlM3cEduUnkwRnV3QTh0VVRmN2p4RHdNTklIYkZZOG01dTRmWDhNd2ku", "remember_me": True, "bio": "This is User 1's bio.", "firstName": "Alex", "lastName": "White"},
    "d5377bb4777aa34c": {"userID": "d5377bb4777aa34c", "username": "user2", "password": "JDJiJDEyJFdjOVlPRHMuTzVjRkJkOUFlMUVEVHUyMm5IRVVRUEZScjJwNFh6UFRpME1QWnA2clU3Nmtt", "remember_me": True, "bio": "Welcome to User 2's personal bio page.", "firstName": "John", "lastName": "Black"},
    "af14b1a7f613ee85": {"userID": "af14b1a7f613ee85", "username": "user3", "password": "JDJiJDEyJEhYMy5UaG9HSGJrcmE2TkdWaVEuek9ESzFFaEJWVkRpcnRiQU40TXUwd3dTejZvay9odFJ1", "remember_me": True, "bio": "Welcome to User 3's personal bio page.", "firstName": "Bob", "lastName": "Brown"},
    "1994e7bd59529e6e": {"userID": "1994e7bd59529e6e", "username": "user4", "password": "JDJiJDEyJHBXWTduSWxuWjZCLjMuNTU1VkNEaWVDQ3MxRk5aOW5BblRlUnhSVGsuRXl2RHNYeVIzcVRT", "remember_me": True, "bio": "Welcome to User 4's personal bio page.", "firstName": "Alice", "lastName": "Green"},
}
TUTORS = {
    "4b98eaa33787b050": {"tutorID": "4b98eaa33787b050", "userID": "af14b1a7f613ee85", "qualifications": None, "available_time": None, "active_courses": None, "evaluation": None},
    "32a28baa6ad9e84b":  {"tutorID": "32a28baa6ad9e84b", "userID": "1994e7bd59529e6e", "qualifications": None, "available_time": None, "active_courses": None, "evaluation": None}
}

TOKENS = [123, 321]

def find_user_by_username(username: str):
    for user in USERS.values():
        if user["username"] == username:
            return user
    return {}

def find_user_by_id(user_id: str):
    return USERS.get(user_id, {})

def find_tutor_by_user_id(user_id: str):
    return next((tutor for tutor in TUTORS.values() if tutor["userID"] == user_id), None)

def save_user(user_data):
    pass

def users_with_remember_me():
    return [details for details in USERS.values() if details["remember_me"]]

def get_user_ids():
    return [user["userID"] for user in USERS.values()]

def get_tutor_ids():
    return [tutor["tutorID"] for tutor in TUTORS.values()]

def add_student_to_course(student, course):
    pass

def register_token_exists(register_token: int):
    return register_token in TOKENS

def remove_register_token(register_number):
    pass

def save_tutor(tutor_data):
    pass
