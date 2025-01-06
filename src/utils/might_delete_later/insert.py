#from multiprocessing.reduction import duplicate
from typing import Any, Dict, List, Tuple
from src.utils.data_base_util import DataBaseUtil

class DublicateError(Exception):
    pass

class InsertData(DataBaseUtil):
    def __init__(self):
        super().__init__()

    def insert_one(self, table_name: str, obj: Dict[str, any], condition: str, dublicate: bool = False) -> None:
        try:
            query = f"SELECT 1 FROM {table_name} WHERE {condition} = %s;"
            self.cursor.execute(query, (obj[condition],))
            exists = self.cursor.fetchone()

            if exists and not dublicate:
                raise DublicateError(f"Duplicate entry already exists for {condition}: {obj[condition]}")

            columns = obj.keys()
            values = tuple(obj.values())
            placeholders = ", ".join(["%s"] * len(columns))
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders});"
            self.cursor.execute(insert_query, values)
            self.connection.commit()
            print(f"Object inserted successfully into {table_name}: {obj[condition]}")

        except DublicateError as e:
            print(e)
            raise e
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Error inserting {table_name}: {e}")

    def _insert_many(self, table_name: str, objects: List[Dict[str, any]], condition: str, dublicate: bool = False) -> None:
        errors = []
        for obj in objects:
            try:
                self.insert_one(table_name, obj, condition, dublicate)
            except DublicateError as e:
                if not dublicate:
                    print(f"Skipping duplicate object: {obj}")
            except Exception as e:
                errors.append((obj, str(e)))

        if errors:
            print(errors)
            for obj, err in errors:
                print(f"Error inserting {table_name}: {err}")


if __name__ == '__main__':
    inserter = InsertData()

    obj1 = {"userid": 202345671, "username": "arthur_morgan", "password": "password123", "usertyp": "student", "remember_me": "TRUE"}

    objects = [
        {"userid": 202345672, "username": "john_doe", "password": "newpassword", "usertyp": "admin","remember_me": "TRUE"},
        {"userid": 202345673, "username": "jane_doe", "password": "mypassword", "usertyp": "admin","remember_me": "TRUE"},
        {"userid": 202345671, "username": "arthur_morgan", "password": "password123", "usertyp": "student", "remember_me": "TRUE"}
    ]

    try:
        inserter.insert_one("tmuser", obj1, condition="userid", dublicate=True)
        #inserter.insert_many("tmuser", objects, condition="id", dublicate=False)

    except DublicateError as e:
        print(e)