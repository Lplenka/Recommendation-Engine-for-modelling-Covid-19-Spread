import numpy as np
import random
from typing import List, Set, Tuple

from history import History
from store import Store
from store_path import StorePath

Vector = List[float]
TupleInt = Tuple[int, int]


class Customer:
    def __init__(self, config: dict, items: Set[int], store: Store) -> None:
        """Constructs a customer with store locations to visit"""
        self.config = config
        self.visits = self.__convert_items_to_visits(items)
        # generate path and init positions, etc
        self.path = StorePath(self.visits, store, config)
        self.position_ix = 0
        self.position = self.path.nodes_path[self.position_ix]
        self.wait_timer = self.path.wait_times[self.position_ix]
        # set infection status and duration
        self.infection_status = self.__get_initial_infection_status()
        self.infection_duration = self.__get_initial_infection_duration()
        # results stuff
        self.exposure_time = 0
        self.shopping_time = 0

    def __convert_items_to_visits(self, items: Set[int]) -> List[TupleInt]:
        # load required config values
        items_per_section = self.config['store']['items_per_section']
        n_shelves = self.config['store']['n_shelves']
        # convert items to visits
        visits = []
        for item in items:
            # convert item to section
            section = (item - 1) // items_per_section
            # convert section to aisle and shelf indices
            aisle_ix = section // n_shelves
            shelf_ix = section % n_shelves
            visits.append((aisle_ix, shelf_ix))
        return visits
    
    def reset_customer(self) -> None:
        """Resets the customer's variables"""
        self.position_ix = 0
        self.position = self.path.nodes_path[self.position_ix]
        self.wait_timer = self.path.wait_times[self.position_ix]
        self.infection_status = self.__get_initial_infection_status()
        self.infection_duration = self.__get_initial_infection_duration()
        self.exposure_time = 0
        self.shopping_time = 0

    def __get_initial_infection_status(self) -> None:
        """Gets the initial infection status of the customer"""
        return bool(np.random.binomial(n=1, p=self.config['infection']['init_prob']))
    
    def __get_initial_infection_duration(self) -> int:
        """Gets the initial infection duration of the customer"""
        if not self.infection_status:
            return 0
        else:
            return random.randint(*self.config['infection']['duration_range'])

    def update_position(self) -> None:
        """Updates the customer's position this tick"""
        if self.wait_timer > 0:
            self.wait_timer -= 1
        elif (self.position_ix + 1) >= len(self.path.nodes_path):
            self.position = None
        else:
            self.position_ix += 1
            self.position = self.path.nodes_path[self.position_ix]
            self.wait_timer = self.path.wait_times[self.position_ix]

    def get_position(self) -> int:
        """Returns the position of the customer"""
        return self.position

    def has_left_store(self) -> bool:
        """Returns whether or not the customer has left the store"""
        return self.position is None

    def has_just_infected(self, other: "Customer", history: History) -> bool:
        """Check if this customer will infect the other customer this tick and update accordingly"""
        if self.get_position() is None or other.get_position() is None:
            return False
        if self.get_position() != other.get_position():
            return False
        if not self.is_infected() or other.is_infected():
            return False
        if self.infection_duration == 0:
            return False
        self.exposure_time += 1
        other.exposure_time += 1
        history.add_exposure_time(self.get_position())
        if random.uniform(0, 1) <= self.__calc_trans_prob():
            other.set_infected()
            return True
        else:
            return False
    
    def is_infected(self) -> bool:
        """Returns the infection status of the customer"""
        return self.infection_status

    def set_infected(self) -> None:
        """Marks the customer as infected (but with a duration of 0 so they can't infect anyone else)"""
        self.infection_status = True
        self.infection_duration = 0

    def __calc_trans_prob(self) -> float:
        """Calculates the probability of transmission"""
        R0 = self.config['infection']['R0']
        average_contacts = self.config['infection']['average_contacts']
        return R0 / (average_contacts * self.infection_duration)
