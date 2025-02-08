import unittest
from secrets import token_hex
from src.backend.room import Room


class TestRoom(unittest.TestCase):

    def test_add_new_room_success(self):
        room_name = token_hex(8)
        room_id = Room.add_new_room(room_name)

        room = Room.get_room_by_id(room_id)

        self.assertIsNotNone(room)
        self.assertEqual(room.name, room_name)

    def test_get_room_by_id_not_found(self):
        non_existent_room_id = "non_existent_room_id"
        room = Room.get_room_by_id(non_existent_room_id)

        self.assertIsNone(room)

    def test_get_rooms_by_name_prefix(self):
        matching_rooms = Room.get_rooms_by_name_prefix("Lecture Hall")

        self.assertEqual(len(matching_rooms), 4)
        self.assertTrue(all(room.name.startswith("Lecture Hall") for room in matching_rooms))

        matching_room_names = [room.name for room in matching_rooms]
        self.assertIn("Lecture Hall 1", matching_room_names)
        self.assertIn("Lecture Hall 2", matching_room_names)
        self.assertNotIn("Maximum", matching_room_names)

if __name__ == "__main__":
    unittest.main()