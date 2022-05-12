from xmlrpc.client import Boolean
import numpy as np
import random
import time
from typing import List, Set, Tuple

from store import Store
from store_path import StorePath

Vector = List[float]
TupleInt = Tuple[int, int]


class Customer:
    def __init__(self, config: dict, items: Set[int], store: Store) -> None:
        """Constructs a customer with store locations to visit"""
        self.config = config
        self.visits = self.__convert_items_to_visits(items)
        # generate path and node times
        self.path = StorePath(self.visits, store)
        self.node_wait_time = [
            random.randint(1, 10)
            for _ in self.path.nodes_visit
        ]
        self.current_node_wait_time = self.node_wait_time[0]
        self.position = (self.path.nodes_visit[0], time.time())
        self.node_wait_timer = 0
        # set infection status
        self.infection_duration = 0
        self.infection_status = False

    def __convert_items_to_visits(self, items: Set[int]) -> List[TupleInt]:
        # load required config values
        items_per_section = self.config['store']['items_per_section']
        n_sections = self.config['store']['n_sections']
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

    def __set_initial_infected_status(self) -> bool:
        """Determine the initial infection status for this customer"""
        return False

    def is_infected(self) -> bool:
        """Returns whether or not the customer is infected"""
        # set self.infection_duration (any number between 1 to 7)
        status = np.random.binomial(size=1, n=1, p=229.9/100000)
        if status[0] == 0:
            self.infection_status = False
            return False
        else:
            self.infection_status = True
            return True

    def update_visit_probabilities() -> None:
        """Updates item purchase probabilities based on most recent item purchases"""
        return

    def __init_position(self) -> None:
        """Initialises the customer's position"""
        return

    def update_position(self) -> None:
        """Updates the customer's position this tick"""
        curr_node = self.position[0]
        curr_node_index = self.path.nodes_visit.index(curr_node)

        if (self.current_node_wait_time > self.node_wait_timer):
            self.node_wait_timer += 1
            return

        if self.path.nodes_visit[curr_node_index] == self.path.nodes_visit[-1]:
            return
        self.position = (self.path.nodes_visit[curr_node_index+1], time.time())
        print('Paths to visit:', self.path.nodes_visit, 'Position:',
              self.position[0], 'after', self.current_node_wait_time, 'ticks')
        self.node_wait_timer = 0
        self.current_node_wait_time = self.node_wait_time[curr_node_index+1]
        return

    def get_position(self) -> TupleInt:
        """Returns the current position of the customer"""
        return self.position

    def has_left_store(self) -> bool:
        """Returns whether or not the customer left the store this tick"""
        return False

    def calculate_transmissibility(self, R0, average_contacts, duration) -> float:
        """Calculates the transmissibility or probability of transmission"""
        return R0/(average_contacts*duration)

    def get_infection_duration(self) -> int:
        """Returns the duration for which the customer has been infected"""
        if (self.infection_status):
            self.infection_duration = random.randint(1, 7)
        else:
            self.infection_duration = 0
        return self.infection_duration

    def set_infection_duration(self, duration) -> None:
        """Sets the duration for which the customer has been infected(all customers infected in the simulation run would be given a value of 0)"""
        self.infection_duration = duration
        return

    def set_simulation_infection(self) -> None:
        self.infection_status = True
        return

    def update_infection_probability(self, other_customer: "Customer", tick_count = 0) -> bool:
        """Update this customer's infection prob. based on other customer's distance and infection status"""
        

        if not (self.is_infected() == other_customer.is_infected()):
            
            if (self.get_position()[0] == other_customer.get_position()[0]) and (tick_count - self.get_position()[1]) > 1 and (tick_count - other_customer.get_position()[1]) > 1: 
            
                choices = [True, False]

                if (self.is_infected() and self.get_infection_duration() != 0):
                    transmissibility = self.calculate_transmissibility(
                        2.5, 3, self.get_infection_duration())

                    distribution = [transmissibility, 1 - transmissibility]
                    if random.choices(choices, distribution)[0]:
                        other_customer.set_simulation_infection()
                        return True
       
                elif (other_customer.is_infected() and other_customer.get_infection_duration() != 0):
                    transmissibility = other_customer.calculate_transmissibility(
                        2.5, 3, other_customer.get_infection_duration())
                    distribution = [transmissibility, 1 - transmissibility]
                    if random.choices(choices, distribution)[0]:
                        self.set_simulation_infection()
                        return True

        return False
