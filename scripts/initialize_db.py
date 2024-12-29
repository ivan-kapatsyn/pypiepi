# scripts/initialize_db.py
from src.utils.data_base_util import DataBaseUtil
from src.utils.env_variable_util import EnvVariableUtil
from pathlib import Path

if __name__ == "__main__":
    db_util = DataBaseUtil()

    # Absolute path to the JSON file containing database structure
    base_path = Path(__file__).resolve().parents[1]  # Zwei Ebenen über 'utils'
    json_file_path = base_path / "data_folder" / "database_structure.json"

    if not json_file_path.exists():
        raise FileNotFoundError(f"The JSON file {json_file_path} was not found.")

    try:
        # Initialize the database
        db_util.initialise(json_file_path)
    except Exception as e:
        print(f"Error initializing the database: {e}")
    finally:
        # Closing the connection
        if db_util:
            print("Closing the connection...")
            del DataBaseUtil
