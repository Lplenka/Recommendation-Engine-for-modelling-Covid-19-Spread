import random
import scipy.stats as stats
import time
from csv import reader
from functools import reduce
from typing import List, Optional, Set
from visualizer import Visualizer
from config import get_full_config
from customer import Customer
from store import Store


class Simulation:
    def __init__(self, config: dict = None) -> None:
        """Initialises the simulation"""
        self.config = get_full_config(config)
        self.__set_random_seed()
        self.store = Store(self.config)
        self.customers = self.__generate_customers()
        self.tick_count = 0

    def __set_random_seed(self) -> None:
        """Sets the random seed to make simulations repeatable"""
        if self.config['seed'] is None:
            self.config['seed'] = str(time.time())
        random.seed(self.config['seed'])

    def __generate_customers(self) -> List[Customer]:
        # load visited items for each customer
        customer_items = self.__load_customer_dataset()
        n_customers = len(customer_items)
        # shuffle the order of the customers for added randomness
        random.shuffle(customer_items)
        # generate and return a list of customer objects
        return [
            Customer(self.config, customer_items[i], self.store)
            for i in range(n_customers)
        ]

    def __load_customer_dataset(self) -> List[Set[int]]:
        """Loads a set of items for each customer from the csv dataset"""
        customer_items = []
        with open(self.config['customers']['dataset_path'], 'r', newline='') as f:
            csv_reader = reader(f, delimiter=',')
            next(csv_reader, None)  # skip the header
            for row in csv_reader:
                customer_items.append(
                    eval(row[2].replace('\'', ''))
                )
        return customer_items

    def start_day_simulation(self) -> None:
        """Initialise a day's simulation"""
        self.customers_in_store = []
        self.customers_who_visited = []

    def end_day_simulation(self) -> None:
        """Finalise a day's simulation"""
        for customer in self.customers_who_visited:
            customer.update_visit_probabilities()

    def get_tick_count(self) -> int:
        """returns tick count"""
        return self.tick_count

    def set_tick_count(self) -> None:
        self.tick_count += 1
        return None

    def tick(self) -> None:
        """Simulate a tick in a day's simulation"""
        # add next customer if needed
        self.set_tick_count()
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
        customer_arrival_probability = stats.gamma.pdf(
            self.get_tick_count(), a=6, scale=1.5)*6
        choices = [True, False]
        distribution = [customer_arrival_probability,
                        1 - customer_arrival_probability]
        if random.choices(choices, distribution):
            return self.customers[self.get_tick_count()]
    
    def test_path_generation(self):
        visualizer = Visualizer(self.config, self.store)
        visualizer.run()


if __name__ == '__main__':
    sim = Simulation()
    #visualizer = Visualizer(sim.config, sim.store)
    #sim.start_day_simulation()
    #for i in range(10):
        #print('Tick', sim.get_tick_count())
        #sim.tick()
        #visualizer.add_customers(sim.customers_in_store)
    #visualizer.run()
    # have to fix end day simulation to update probabilities of each customer in the csv based on thir buys.
    # sim.end_day_simulation()
    #time.sleep(0.5)
