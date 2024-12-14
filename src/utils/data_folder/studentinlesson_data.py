import csv
from src.utils.data_base_util import DataBaseUtil
import psycopg2

data = [
    ["lessonid", "studentid"],
    [5432,202345671],
    [5432,202345672],
]

csv_file = "../../../data_folder/studentinlesson_table_data.csv"

try:
    with open(csv_file, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    print("Data written successfully")
except Exception as error:
    print(f"Error: {error}")


class AddToUser(DataBaseUtil):
    def __init__(self):
        super().__init__('postgres', 'postgres', 'melisahu', 'localhost', 5432, )

    def import_csv(self, csv_file):
        try:
            with (open(csv_file, mode='r', encoding="utf-8") as csvfile):
                reader = csv.reader(csvfile)
                next(reader, None)

                for row in reader:
                    print(f"Row: {row}")
                    insert_query = f"INSERT INTO studentinlesson (lessonid, studentid) VALUES ({row[0]}, '{row[1]}');"
                    self.cursor.execute(insert_query)

            self.connection.commit()
            print("Data imported successfully")
        except Exception as e:
            print(f"Error: {e}")
            self.connection.rollback()
            raise


if __name__ == "__main__":
    try:
        add_to_user = AddToUser()
        add_to_user.import_csv("../../../data_folder/studentinlesson_table_data.csv")
    except Exception as error:
        print(f"Error: {error}")
