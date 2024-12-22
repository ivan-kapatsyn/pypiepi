from typing import List, Optional

class Evaluation:
    def __init__(self, ratings: Optional[List[int]] = None):
        self.ratings = ratings or []
