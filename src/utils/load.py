from typing import Any, Dict, List, Callable, Tuple
import psycopg2
from src.utils.data_base_util import DataBaseUtil

class LoadError(Exception):
    pass


class DataLoader(DataBaseUtil):
    def __init__(self):
        super().__init__('postgres', 'postgres', 'melisahu', 'localhost', 5432, )

    def fetch_one(self, query: str, params: Tuple[Any, ...] = ()) -> Dict[str, Any]:
        try:
            self.cursor.execute(query, params)
            result = self.cursor.fetchone()
            if result:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
            return None
        except Exception as error:
            raise Exception(f"Fehler beim Ausführen von fetch_one: {error}")


    def fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            if results:
                columns = [desc[0] for desc in self.cursor.description]
                return [dict(zip(columns, row)) for row in results]
            return []
        except Exception as error:
            raise Exception(f"Fehler beim Ausführen von fetch_all: {error}")

    def load_data(self, table_name: str, condition: str, value:any ) -> Dict[str, Any]:
        query = f'SELECT * FROM {table_name} WHERE {condition} = %s;'
        result = self.fetch_one(query, (value,))

        if not result:
            raise LoadError(f"No entry found where {condition} = {value}.")
        return result

    def load_many(self, table_name: str, filter_function: Callable[[Dict[str,Any]], bool]) -> List[Dict[str, Any]]:

        query = f'SELECT * FROM {table_name};'
        results = self.fetch_all(query)
        return [result for result in results if filter_function(result)]

    #def filter_function(obj):
    #    return obj['username'].startswith('A')


loader = DataLoader()
try:
    user = loader.load_data('tmuser', 'userid', 202345671)
    print(user)
except LoadError as e:
    print(e)

#users = loader.load_many('user', filter_function)
#print(users)