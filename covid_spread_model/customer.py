import random
from typing import List, Tuple

Vector = List[float]
TupleInt = Tuple[int, int]


class Customer:
    def __init__(self, config: dict) -> None:
        """Constructs a customer with store locations to visit"""
        self.config = config
        self.visits = self.__get_visits()
        self.path = None
    
    def __get_visits(self) -> List[TupleInt]:
        """Generates a non-empty list of random store locations to visit"""
        pcv_sections = self.config['store']['pc_visit_sections']
        pcv_shelves = self.config['store']['pc_visit_shelves']
        visits = []
        for i, pcv_section in enumerate(pcv_sections):
            if random.uniform(0, 1) >= pcv_section: continue
            for j, pcv_shelf in enumerate(pcv_shelves[i]):
                if random.uniform(0, 1) >= pcv_shelf: continue
                visits.append((i, j))
        # if the customer isn't visiting any locations then regenerate the list
        if len(visits) == 0:
            visits = self.__get_visits()
        return visits

    def __get_visits_custom(self) -> List[TupleInt]:
        """Generates a non-empty list of random store locations to visit"""
        return []
    
    def __set_initial_infected_status(self) -> bool:
        """Determine the initial infection status for this customer"""
        return False
    
    def is_infected(self) -> bool:
        """Returns whether or not the customer is infected"""
        return False
    
    def update_visit_probabilities() -> None:
        """Updates item purchase probabilities based on most recent item purchases"""
        return

    def __init_position(self) -> None:
        """Initialises the customer's position"""
        return
    
    def update_position(self) -> None:
        """Updates the customer's position this tick"""
        return
    
    def get_position(self) -> TupleInt:
        """Returns the current position of the customer"""
        return (0, 0)
    
    def has_left_store(self) -> bool:
        """Returns whether or not the customer left the store this tick"""
        return False
    
    def update_infection_probability(self, other_customer: "Customer"):
        """Update this customer's infection prob. based on other customer's distance and infection status"""
        return
