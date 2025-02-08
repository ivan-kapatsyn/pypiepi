from typing import Optional, List
from secrets import token_hex
from src.utils.data_base_util import DataBaseUtil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Room:
    def __init__(self, room_id: str, name: str):
        self.room_id = room_id
        self.name = name

    @staticmethod
    def add_new_room(name: str) -> str:
        """
        Adds a new room to the database.

        Args:
            name (str): The name of the room to add.

        Returns:
            str: The unique ID of the newly created room.
        """
        room_id = Room._generate_unique_room_id()

        db = DataBaseUtil()
        db.insert_one("room", {"room_ID": room_id, "name": name}, "room_ID")
        logger.info(f"Room '{name}' added successfully with ID '{room_id}'.")

        return room_id

    @classmethod
    def get_room_by_id(cls, room_id: str) -> Optional["Room"]:
        """
        Retrieves a room by its unique ID.

        Args:
            room_id (str): The unique ID of the room to retrieve.

        Returns:
            Optional[Room]: The Room instance if found, otherwise None.
        """
        room_data = cls._find_room_by_id(room_id)
        if room_data is None:
            logger.warning(f"No room found with ID '{room_id}'.")
            return None

        return cls(*room_data)

    @classmethod
    def get_rooms_by_name_prefix(cls, name_prefix: str) -> List["Room"]:
        """
        Retrieves a list of rooms whose names start with the given prefix.

        Args:
            name_prefix (str): The prefix to match room names against.

        Returns:
            List[Room]: A list of Room instances whose names start with the given prefix.
        """
        db = DataBaseUtil()
        search_value = f"{name_prefix}%"
        results = db.load_many("room", "name LIKE %s", [search_value])

        rooms = [cls.get_room_by_id(record[0]) for record in results]
        return rooms

    @staticmethod
    def _find_room_by_id(room_id: str) -> Optional[List]:
        db = DataBaseUtil()
        try:
            data = db.load_one("room", "room_ID", room_id)
        except Exception as e:
            data = None
        return data

    @staticmethod
    def _generate_unique_room_id() -> str:
        db = DataBaseUtil()
        existing_ids = {room[0] for room in db.load_many("room")}
        while True:
            room_id = token_hex(8)
            if room_id not in existing_ids:
                return room_id