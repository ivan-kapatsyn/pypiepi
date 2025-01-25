from datetime import datetime

class Evaluation:
    def __init__(self, evaluation_id: str, author, date: datetime, numeric_evaluation: int, feedback: str):
        self.evaluation_id = evaluation_id
        self.author = author
        self.date = date
        self.numeric_evaluation = numeric_evaluation
        self.feedback = feedback
