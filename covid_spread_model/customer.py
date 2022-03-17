import random
from typing import List, Tuple

Vector = List[float]
TupleInt = Tuple[int, int]


class Customer:
    def __init__(self, config: dict) -> None:
        """Constructs a customer with store locations to visit"""
        pcv_sections = config['store']['pc_visit_sections']
        pcv_shelves = config['store']['pc_visit_shelves']
        self.visits = self.__get_visits(pcv_sections, pcv_shelves)
    
    def __get_visits(self, pcv_sections: Vector, pcv_shelves: List[Vector]) -> List[TupleInt]:
        """Generates a non-empty list of random store locations to visit"""
        visits = []
        for i, pcv_section in enumerate(pcv_sections):
            if random.uniform(0, 1) >= pcv_section: continue
            for j, pcv_shelf in enumerate(pcv_shelves[i]):
                if random.uniform(0, 1) >= pcv_shelf: continue
                visits.append((i, j))
        # if the customer isn't visiting any locations then regenerate the list
        if len(visits) == 0:
            visits = self.__get_visits(pcv_sections, pcv_shelves)
        return visits
