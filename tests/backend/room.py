import unittest
from src.backend.room import Room


class TestRoom(unittest.TestCase):

    def test_add_new_room_success(self):
        room_name = "Lecture Hall 1"
        room_id = Room.add_new_room(room_name)

        room = Room.get_room_by_id(room_id)

        self.assertIsNotNone(room)
        self.assertEqual(room.name, room_name)

    def test_get_room_by_id_not_found(self):
        non_existent_room_id = "non_existent_room_id"
        room = Room.get_room_by_id(non_existent_room_id)

        self.assertIsNone(room)

if __name__ == "__main__":
    unittest.main()