import unittest
from secrets import token_hex
from src.backend.evaluation import Evaluation


class TestEvaluation(unittest.TestCase):

    def test_get_evaluations_by_course_ids(self):
        course_ids = ["dc295cc4dd09d5b1", "39104442b2660b56"]
        evaluations = Evaluation.get_evaluations_by_course_ids(course_ids)

        self.assertEqual(len(evaluations), 3)
        self.assertIn(evaluations[0].course_id, course_ids)
        self.assertIn(evaluations[1].course_id, course_ids)
        self.assertIn(evaluations[2].course_id, course_ids)

    def test_get_evaluations_by_course_ids_invalid(self):
        course_ids = ["invalid_id"]
        evaluations = Evaluation.get_evaluations_by_course_ids(course_ids)

        self.assertEqual(len(evaluations), 0)

    def test_get_by_id(self):
        evaluation_id = "46733e77c313bf45"
        evaluation = Evaluation.get_by_id(evaluation_id)

        self.assertIsNotNone(evaluation)
        self.assertEqual(evaluation.evaluation_id, evaluation_id)
        self.assertEqual(evaluation.course_id, "39104442b2660b56")

    def test_get_by_id_invalid(self):
        evaluation_id = "invalid_id"
        evaluation = Evaluation.get_by_id(evaluation_id)

        self.assertIsNone(evaluation)

if __name__ == "__main__":
    unittest.main()