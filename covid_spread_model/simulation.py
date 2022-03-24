import random
import time
from typing import List, Optional

from config import get_full_config
from customer import Customer
from store import Store
from store_path import StorePath
from visualizer import Visualizer


class Simulation:
    def __init__(self, config: dict = None) -> None:
        """Initialises the simulation"""
        self.config = get_full_config(config)
        self.__set_random_seed()
        self.store = Store(self.config)
        self.customers = self.__generate_customers()

    def __set_random_seed(self) -> None:
        """Sets the random seed to make simulations repeatable"""
        if self.config['seed'] is None:
            self.config['seed'] = str(time.time())
        random.seed(self.config['seed'])
    
    def __generate_customers(self) -> List[Customer]:
        """Generates a list of all possible customers"""
        return [
            Customer(self.config)
            for _ in range(self.config['customers']['n_customers'])
        ]
    
    def start_day_simulation(self) -> None:
        """Initialise a day's simulation"""
        self.customers_in_store = []
        self.customers_who_visited = []
    
    def end_day_simulation(self) -> None:
        """Finalise a day's simulation"""
        for customer in self.customers_who_visited:
            customer.update_visit_probabilities()

    def tick(self) -> None:
        """Simulate a tick in a day's simulation"""
        # add next customer if needed
        next_customer = self.__get_next_customer()
        if next_customer is not None:
            self.customers_in_store.append(next_customer)
            self.customers_who_visited.append(next_customer)
        # update all customers positions and infection probabilities
        for customer in self.customers_in_store:
            customer.update_position()
        for customer1 in self.customers_in_store:
            for customer2 in self.customers_in_store:
                if customer1 != customer2:
                    customer1.update_infection_probability(customer2)
        # remove customers who just left the store
        remaining_customers_in_store = []
        for customer in self.customers_in_store:
            if not customer.has_left_store():
                remaining_customers_in_store.append(customer)
        self.customers_in_store = remaining_customers_in_store

    def __get_next_customer(self) -> Optional[Customer]:
        """Determine if a new customer will join the queue this tick and return them from the list"""
        return None

    def test_path_generation(self) -> None:
        """Temporary method for testing path generation and visualization"""
        customer = Customer(self.config)
        store_path = StorePath(customer, self.store)
        visualizer = Visualizer(self.config, self.store)
        visualizer.add_path(store_path)
        visualizer.run()


if __name__ == '__main__':
    sim = Simulation()
    sim.test_path_generation()
