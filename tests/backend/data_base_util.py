import os
import unittest
from pandas.core.interchange import column
from src.utils.data_base_util import DataBaseUtil
from src.utils.env_variable_util import EnvVariableUtil
from src.utils.path_util import PathUtil


class DataBaseUtilTestCase(unittest.TestCase):

    def setUp(self):
        self.db_util = DataBaseUtil()

#WORK
    def test_initialise(self):
        self.db_util.initialise()

#WORKS
    def test_if_exist(self):
        table_name = 'users'
        self.assertEqual(self.db_util._check_if_table_exists(
                table_name), True)

#WORK
    def test_load_one(self):
        table_name = 'users'
        column = "user_id"
        id_value = "f63b0b2f7c48c85f"

        expected_result = ["f63b0b2f7c48c85f", "arthur.morgan",
                           "JDJiJDEyJGx6RjZMbnZqTEdJcEtlY3pWZENqNmVWQkpKcnVSSGNSaU54S085TWQvc2tYQ29FQWF6d2wy",
                           "arthur", "morgan", "NaN",True]
        self.assertEqual(self.db_util.load_one(table_name, column,id_value), expected_result)

#WORK
    def test_load_many(self):
        table_name = 'users'
        filter_function = "first_name = %s"
        user_first_name = ["john"]

        expected_result = [
            [
                "f67d38dee48d641f",
                "john.doe",
                "JDJiJDEyJHB6L3o4ZnR3SE1uQkpzS09UUUpSaS5pLzRvYks1OTVSL0s3NXVnOVVmRlFVcXp3YTkzUzNP",
                "john",
                "doe",
                "Shrek is love. Shrek is live",
                True
            ],
            [
                "59d1dcf2a970a9fd",
                "john.marston",
                "JDJiJDEyJDgxaXUuZmdNZXVPcHJCYXQveEwyRS51UVZKZ1UwLnBXVDdIVnBBQVRPdVNQWXluSm45SENT",  # password
                "john",
                "marston",
                "NaN",
                False
            ]
        ]

        result = self.db_util.load_many(table_name, filter_function, user_first_name)
        self.assertEqual(result, expected_result)


#WORK
    def test_insert_one(self):
        new_user_id = self.db_util.generate_unique_id()
        obj1 = {
            "user_id": new_user_id,
            "username": "eren.jaeger",
            "password": "thisismypassword",
            "first_name": "eren",
            "last_name": "jaeger",
            "bio": "tatakai! tatakai!",
            "remember_me": True
        }

        self.db_util.insert_one("users", obj1, column="user_id", dublicate=True)

        loaded_data = self.db_util.load_one("users",  "user_id", value=new_user_id)

        self.assertEqual(loaded_data['user_id'], new_user_id)
        self.assertEqual(loaded_data['username'], obj1['username'])
        self.assertEqual(loaded_data['bio'], obj1['bio'])


#WORK
    def test_insert_user(self):
        new_user_id = self.db_util.generate_unique_id()
        obj_user = {
            "user_id": new_user_id,
            "username": "johnny.silverhand",
            "password": "thisismypassword",
            "first_name": "johnny",
            "last_name": "silverhand",
            "bio": "fuck arasaka",
            "remember_me": False
        }

        self.db_util.insert_one("users", obj_user, column="user_id", dublicate=True)
        loaded_data = self.db_util.load_one("users",  "user_id", new_user_id)
        self.assertEqual(loaded_data['user_id'], new_user_id)
        self.assertEqual(loaded_data['username'], "johnny.silverhand")
        self.assertEqual(loaded_data['first_name'], "johnny")
        self.assertEqual(loaded_data['last_name'], "silverhand")
        self.assertEqual(loaded_data['bio'], "fuck arasaka")
        self.assertEqual(loaded_data['remember_me'], False)

#WORK
    def test_insert_many(self):
        new_user_id = self.db_util.generate_unique_id()
        objects = [
            {
                "user_id": new_user_id,
                "username": "mr.bean",
                "password": "thisismypassword",
                "first_name": "mr",
                "last_name": "bean",
                "bio": "teddy",
                "remember_me": True
            },
            {
                "user_id": new_user_id,
                "username": "bird.eren",
                "password": "thisismypassword",
                "first_name": "eren",
                "last_name": "jaeger",
                "bio": "krah! krah!",
                "remember_me": False
            }
        ]
        self.db_util.insert_many("users", objects, column="user_id", dublicate=True)

        for obj in objects:
            loaded_data = self.db_util.load_one("users", "user_id", obj["user_id"])
            self.assertEqual(loaded_data['username'], obj['username'])
            self.assertEqual(loaded_data['remember_me'], obj['remember_me'])

# WORK
    def test_insert_with_duplicate_true(self):
        new_user_id = self.db_util.generate_unique_id()
        obj = {
                    "user_id": new_user_id,
                    "username": "charles.smith",
                    "password": "thisismypassword",
                    "first_name": "charles",
                    "last_name": "smith",
                    "bio": "",
                    "remember_me": True
                }
        self.db_util.insert_one('users', obj, 'user_id', dublicate=True)

# WORK
    def test_insert_with_duplicate_false(self):
        new_user_id = self.db_util.generate_unique_id()
        obj = {
                    "user_id": new_user_id,
                    "username": "dutch.vanderlinde",
                    "password": "tahiti",
                    "first_name": "dutch",
                    "last_name": "van der linde",
                    "bio": "",
                    "remember_me": True
                }
        self.db_util.insert_one('users', obj, 'user_id', dublicate=False)

# WORK
    def test_delete_one_with_id(self):
        table_name = 'student'
        id_value = "59d1dcf2a970a9fd"
        self.assertEqual(self.db_util.delete_one_with_id(table_name, id_value), None)

# WORK
    def test_delete_one(self):
        table_name = 'student'
        column_d = "user_id"
        value_d = "16f9cbf0d5f0e513"
        self.assertEqual(self.db_util.delete_one(table_name, column_d, value_d), None)

# WORK
    def test_delete_many(self):
        table_name = 'student'
        column = "user_id"
        user_ids = ["f67d38dee48d641f", "f63b0b2f7c48c85f"]

        for user_id in user_ids:
            exists_before = self.db_util.exists_user_by_id(table_name, user_id)
            print(f"User {user_id} exists before deletion: {exists_before}")

        self.db_util.delete_many(table_name, column, user_ids)

        for user_id in user_ids:
            exists_after = self.db_util.exists_user_by_id(table_name, user_id)
            print(f"User {user_id} exists after deletion: {exists_after}")
            self.assertFalse(exists_after, f"User {user_id} should have been deleted")

#WORK
    def test_update_one(self):
        table_name = 'users'
        column = "user_id"
        id_value = "f63b0b2f7c48c85f"
        new_values = {"username": "arthur.morgan_updated", "remember_me": False}
        self.db_util.update_one(table_name, column, id_value, new_values)

#WORK
    def test_update_many(self):
        table_name = 'users'
        conditions = [
            {"user_id": "14d099c161cf3bea"},
            {"user_id": "928930d566c50b2d"}
            ]
        new_values = [
            {"remember_me": False},
            {"remember_me": False}
            ]
        self.db_util.update_many(table_name, conditions, new_values)
        result = self.db_util.load_many(
            table_name,
            "user_id = %s",
            ["14d099c161cf3bea"]
            )
        self.assertEqual(result[0]["remember_me"], False)

        result = self.db_util.load_many(
            table_name,
            "user_id = %s",
            ["928930d566c50b2d"]
            )
        self.assertEqual(result[0]["remember_me"], False)

#WORK
    def test_build_query_select(self):
        table_name = "users"
        conditions = [("first_name", "john"), ("remember_me", "TRUE")]
        operator = "AND"
        query_type = "SELECT"

        expected_query = "SELECT * FROM users WHERE first_name = %s AND remember_me = %s;"
        expected_params = ["john", "TRUE"]

        query, params = self.db_util._build_query(table_name, conditions, operator, query_type)

        self.assertEqual(query, expected_query)
        self.assertEqual(params, expected_params)


#WORK
    def test_exist_user_id(self):
        user_id_to_test = "202345671"
        expected_exists = False  # Setzen Sie dies auf True, wenn der Benutzer existieren soll

        # Überprüfen Sie, ob der Benutzer existiert
        exists = self.db_util.exists_user_by_id("users", user_id_to_test)
        print(f"User {user_id_to_test} exists: {exists}")  # Debug-Ausgabe

        # Assert, dass der Benutzer wie erwartet existiert oder nicht existiert
        self.assertEqual(exists, expected_exists, f"User {user_id_to_test} existence check failed")

'''
    def test_save_data_to_csv(self):
        data_user = [
            {"username": "arthur.morgan", "password": "password123", "first_name": "arthur", "last_name": "morgan",
             "bio": "", "remember_me": "TRUE"},
            {"username": "john.doe", "password": "newpassword", "first_name": "john", "last_name": "doe",
             "bio": "Shrek is love. Shrek is live", "remember_me": "TRUE"},
            {"username": "jane.doe", "password": "mypassword", "first_name": "jane", "last_name": "doe",
             "bio": "Professional construction enthusiast", "remember_me": "FALSE"},
            {"username": "john.marston", "password": "mypasswordisbetter", "first_name": "john", "last_name": "marston",
             "bio": "", "remember_me": "FALSE"},
            {"username": "mary.stuart", "password": "stupidpassword", "first_name": "mary", "last_name": "stuart",
             "bio": "Am I a pretty girl?", "remember_me": "TRUE"},
            {"username": "walter.white", "password": "heisenberg", "first_name": "walter", "last_name": "white",
             "bio": "Say my name.", "remember_me": "TRUE"},
            {"username": "luke.skywalker", "password": "jedi123", "first_name": "luke", "last_name": "skywalker",
             "bio": "May the force be with you.", "remember_me": "TRUE"},
            {"username": "rick.grimes", "password": "coral123", "first_name": "rick", "last_name": "grimes",
             "bio": "We are the walking dead.", "remember_me": "TRUE"},
            {"username": "jesse.pinkman", "password": "yo1234", "first_name": "jesse", "last_name": "pinkman",
             "bio": "Yeah science!", "remember_me": "FALSE"},
            {"username": "tony.stark", "password": "ironman", "first_name": "tony", "last_name": "stark",
             "bio": "Genius, billionaire, playboy, philanthropist.", "remember_me": "TRUE"},
            {"username": "barney.stinson", "password": "legenwaitforitdary", "first_name": "barney",
             "last_name": "stinson", "bio": "Suit up!", "remember_me": "TRUE"},
            {"username": "ted.mosby", "password": "architect4life", "first_name": "ted", "last_name": "mosby",
             "bio": "", "remember_me": "TRUE"},
            {"username": "patrick.star", "password": "isthiskrustykrab", "first_name": "patrick", "last_name": "star",
             "bio": "No, this is Patrick!", "remember_me": "FALSE"},
            {"username": "spongebob.squarepants", "password": "ilovekrabbypatties", "first_name": "spongebob",
             "last_name": "squarepants", "bio": "", "remember_me": "TRUE"},
            {"username": "luffy.monkey", "password": "pirateking", "first_name": "monkey", "last_name": "d. luffy",
             "bio": "I’m gonna be the Pirate King!", "remember_me": "TRUE"},
            {"username": "sheldon.cooper", "password": "bazinga", "first_name": "sheldon", "last_name": "cooper",
             "bio": "I'm not crazy. My mother had me tested.", "remember_me": "TRUE"},
            {"username": "leonard.hofstadter", "password": "physics123", "first_name": "leonard",
             "last_name": "hofstadter", "bio": "", "remember_me": "FALSE"},
            {"username": "patrick.star", "password": "mayonnaise", "first_name": "patrick", "last_name": "star",
             "bio": "Is mayonnaise an instrument?", "remember_me": "TRUE"},
            {"username": "sandy.cheeks", "password": "karate123", "first_name": "sandy", "last_name": "cheeks",
             "bio": "A squirrel in the sea!", "remember_me": "TRUE"},
            {"username": "max.mustermann", "password": "musterpasswort", "first_name": "max", "last_name": "mustermann",
             "bio": "", "remember_me": "TRUE"},
            {"username": "darth.vader", "password": "darkside", "first_name": "darth", "last_name": "vader",
             "bio": "I am your father.", "remember_me": "TRUE"},
            {"username": "frodo.baggins", "password": "ringbearer", "first_name": "frodo", "last_name": "baggins",
             "bio": "One ring to rule them all.", "remember_me": "TRUE"},
            {"username": "katniss.everdeen", "password": "mockingjay", "first_name": "katniss", "last_name": "everdeen",
             "bio": "May the odds be ever in your favor.", "remember_me": "TRUE"},
            {"username": "harry.potter", "password": "expelliarmus", "first_name": "harry", "last_name": "potter",
             "bio": "The Boy Who Lived.", "remember_me": "FALSE"},
            {"username": "tony.montana", "password": "scarface", "first_name": "tony", "last_name": "montana",
             "bio": "Say hello to my little friend!", "remember_me": "FALSE"},
            {"username": "vito.corleone", "password": "godfather", "first_name": "vito", "last_name": "corleone",
             "bio": "I'm gonna make him an offer he can't refuse.", "remember_me": "TRUE"},
            {"username": "mario.mario", "password": "itsme", "first_name": "mario", "last_name": "mario",
             "bio": "It's-a me, Mario!", "remember_me": "TRUE"},
            {"username": "lara.croft", "password": "raider123", "first_name": "lara", "last_name": "croft",
             "bio": "Adventurer. Archaeologist. Icon.", "remember_me": "TRUE"},
            {"username": "jack.sparrow", "password": "savvy", "first_name": "jack", "last_name": "sparrow",
             "bio": "Why is the rum always gone?", "remember_me": "FALSE"},
            {"username": "michael.scott", "password": "thatswhatshesaid", "first_name": "michael", "last_name": "scott",
             "bio": "World's Best Boss.", "remember_me": "TRUE"},
            {"username": "elizabeth.bennet", "password": "prideandprejudice", "first_name": "elizabeth",
             "last_name": "bennet",
             "bio": "Obstinate, headstrong girl!", "remember_me": "FALSE"},
            {"username": "bruce.wayne", "password": "iamthebatman", "first_name": "bruce", "last_name": "wayne",
             "bio": "I am vengeance. I am the night.", "remember_me": "TRUE"},
            {"username": "spock.vulcan", "password": "liveandprosper", "first_name": "spock", "last_name": "vulcan",
             "bio": "Live long and prosper.", "remember_me": "TRUE"},
            {"username": "homer.simpson", "password": "donuts", "first_name": "homer", "last_name": "simpson",
             "bio": "Mmm... donuts.", "remember_me": "FALSE"},
            {"username": "james.bond", "password": "007", "first_name": "james", "last_name": "bond",
             "bio": "The name's Bond. James Bond.", "remember_me": "TRUE"},
            {"username": "elsa.arendelle", "password": "letitgo", "first_name": "elsa", "last_name": "arendelle",
             "bio": "Let it go, let it go.", "remember_me": "TRUE"},
            {"username": "gandalf.grey", "password": "you.shall.not.pass", "first_name": "gandalf", "last_name": "grey",
             "bio": "A wizard is never late.", "remember_me": "TRUE"},
            {"username": "bilbo.baggins", "password": "adventure123", "first_name": "bilbo", "last_name": "baggins",
             "bio": "I'm going on an adventure!", "remember_me": "FALSE"},
            {"username": "wade.wilson", "password": "chimichangas", "first_name": "wade", "last_name": "wilson",
             "bio": "Maximum effort.", "remember_me": "FALSE"},
            {"username": "natasha.romanoff", "password": "blackwidow", "first_name": "natasha", "last_name": "romanoff",
             "bio": "I've got red in my ledger.", "remember_me": "TRUE"},
            {"username": "peter.parker", "password": "spiderman123", "first_name": "peter", "last_name": "parker",
             "bio": "With great power comes great responsibility.", "remember_me": "TRUE"},
            {"username": "steve.rogers", "password": "captainamerica", "first_name": "steve", "last_name": "rogers",
             "bio": "I can do this all day.", "remember_me": "TRUE"},
            {"username": "thor.odinson", "password": "mjolnir", "first_name": "thor", "last_name": "odinson",
             "bio": "God of Thunder.", "remember_me": "TRUE"},
            {"username": "bruce.banner", "password": "hulk123", "first_name": "bruce", "last_name": "banner",
             "bio": "That's my secret, Cap. I'm always angry.", "remember_me": "FALSE"},
            {"username": "diana.prince", "password": "wonderwoman", "first_name": "diana", "last_name": "prince",
             "bio": "I will fight for those who cannot fight for themselves.", "remember_me": "TRUE"},
            {"username": "anakin.skywalker", "password": "darkside123", "first_name": "anakin",
             "last_name": "skywalker",
             "bio": "This is where the fun begins.", "remember_me": "FALSE"},
            {"username": "marty.mcfly", "password": "delorean", "first_name": "marty", "last_name": "mcfly",
             "bio": "Nobody calls me chicken!", "remember_me": "TRUE"},
            {"username": "doc.brown", "password": "greatscott", "first_name": "emmett", "last_name": "brown",
             "bio": "Roads? Where we're going, we don't need roads.", "remember_me": "TRUE"},
            {"username": "tony.montana", "password": "sayhello", "first_name": "tony", "last_name": "montana",
             "bio": "Say hello to my little friend!", "remember_me": "FALSE"},
            {"username": "jason.bourne", "password": "ciaagent", "first_name": "jason", "last_name": "bourne",
             "bio": "I don't remember anything, but I know how to fight.", "remember_me": "FALSE"},
            {"username": "frank.castle", "password": "punisher", "first_name": "frank", "last_name": "castle",
             "bio": "One batch, two batch. Penny and dime.", "remember_me": "FALSE"},
            {"username": "neo.matrix", "password": "thereisnospoon", "first_name": "neo", "last_name": "matrix",
             "bio": "I know kung fu.", "remember_me": "TRUE"},
            {"username": "trinity.matrix", "password": "trinity123", "first_name": "trinity", "last_name": "matrix",
             "bio": "The Matrix cannot tell you who you are.", "remember_me": "TRUE"},
            {"username": "arthur.dent", "password": "dontpanic", "first_name": "arthur", "last_name": "dent",
             "bio": "Don't panic. Always carry a towel.", "remember_me": "FALSE"},
            {"username": "ford.prefect", "password": "galaxy42", "first_name": "ford", "last_name": "prefect",
             "bio": "Time is an illusion. Lunchtime doubly so.", "remember_me": "TRUE"},
            {"username": "hannibal.lecter", "password": "fava_beans", "first_name": "hannibal", "last_name": "lecter",
             "bio": "I do wish we could chat longer, but I'm having an old friend for dinner.", "remember_me": "FALSE"},
            {"username": "buffy.summers", "password": "slayer", "first_name": "buffy", "last_name": "summers",
             "bio": "Into every generation, a Slayer is born.", "remember_me": "TRUE"},
            {"username": "dexter.morgan", "password": "darkpassenger", "first_name": "dexter", "last_name": "morgan",
             "bio": "Blood never lies.", "remember_me": "FALSE"},
            {"username": "meredith.grey", "password": "greysanatomy", "first_name": "meredith", "last_name": "grey",
             "bio": "Pick me. Choose me. Love me.", "remember_me": "TRUE"},
            {"username": "gregory.house", "password": "diagnostics", "first_name": "gregory", "last_name": "house",
             "bio": "Everybody lies.", "remember_me": "FALSE"},
        ]

        # Jede user_id generieren
        for user in data_user:
            user["user_id"] = self.db_util.generate_unique_id()

        column_types = {
            "user_id": "VARCHAR(16)",
            "username": "VARCHAR(200)",
            "password": "VARCHAR(80)",
            "first_name": "VARCHAR(20)",
            "last_name": "VARCHAR(200)",
            "bio": "VARCHAR(200)",
            "remember_me": "BOOLEAN"
        }

        table_name = "users"

        self.db_util.save_data_to_csv(table_name, data_user, column_types)

'''



if __name__ == '__main__':
    unittest.main()
