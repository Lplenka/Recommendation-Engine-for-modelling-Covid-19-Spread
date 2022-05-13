import matplotlib.pyplot as plt
import random
from csv import reader
from scipy.stats import gamma
from typing import List, Optional, Set

from config import get_full_config
from customer import Customer
from history import History
from store import Store
from visualizer import Visualizer


class Simulation:
    def __init__(self, config: dict = None) -> None:
        """Initialises the simulation"""
        self.config = get_full_config(config)
        self.store = Store(self.config)
        self.total_ticks = self.__get_total_ticks()

    def __get_total_ticks(self) -> int:
        """Calculates the number of ticks required to simulate a day"""
        total_seconds = self.config['flow']['hours_open'] * 3600
        total_ticks = total_seconds // self.config['flow']['tick_duration_sec']
        return total_ticks

    def run_n_simulations(self, n_simulations: int) -> None:
        """Runs multiple day simulations and keeps track of the results"""
        self.history = History(n_simulations, self.store, self.total_ticks)
        for i in range(n_simulations):
            print(f'Running simulation {i + 1} of {n_simulations}')
            self.__run()
            self.history.next_simulation()

    def __run(self) -> None:
        """Runs the simulation for a full day"""
        self.__reset_simulation()
        while self.cur_tick < self.total_ticks:
            self.__tick()
            self.cur_tick += 1
            self.history.next_tick()

    def __reset_simulation(self) -> None:
        """Resets simulation-specific variables"""
        # time/flow values
        self.cur_tick = 0
        # customer values
        self.customers = self.__generate_customers()
        random.shuffle(self.customers)
        self.n_customers_who_visited = 0
        self.customers_in_store = []
        self.customers_who_visited = []
        # infection values
        self.n_initial_infected = self.__get_initial_n_infected()
        self.n_newly_infected = 0
        self.n_infected_who_visited = 0
    
    def __generate_customers(self) -> List[Customer]:
        """Generates a randomised list of customers using the CSV dataset"""
        # load visited items for each customer
        customer_items = self.__load_customer_dataset()
        self.n_customers = len(customer_items)
        # generate a list of customer objects
        customers = [
            Customer(self.config, customer_items[i], self.store)
            for i in range(self.n_customers)
        ]
        # return the lsit
        return customers

    def __load_customer_dataset(self) -> List[Set[int]]:
        """Loads a set of items for each customer from the CSV dataset"""
        customer_items = []
        with open(self.config['customers']['dataset_path'], 'r', newline='') as f:
            csv_reader = reader(f, delimiter=',')
            next(csv_reader, None)  # skip the header
            for row in csv_reader:
                customer_items.append(eval(row[2].replace('\'', '')))
        return customer_items

    def __get_initial_n_infected(self) -> int:
        """Returns the number of initially infected customers"""
        return sum(int(customer.is_infected()) for customer in self.customers)

    def __tick(self) -> None:
        """Simulate a tick in a daily simulation"""
        # add next customer if needed
        next_customer = self.__get_next_customer()
        if next_customer is not None:
            self.n_customers_who_visited += 1
            if next_customer.is_infected():
                self.n_infected_who_visited += 1
            self.customers_in_store.append(next_customer)
            self.customers_who_visited.append(next_customer)
        # update customer positions
        for customer in self.customers_in_store:
            customer.update_position()
        # update customer infection probabilities
        for customer1 in self.customers_in_store:
            for customer2 in self.customers_in_store:
                if customer1 != customer2:
                    if customer1.has_just_infected(customer2, self.history):
                        self.n_newly_infected += 1
        # remove customers who just left the store
        new_customers_in_store = []
        for customer in self.customers_in_store:
            if not customer.has_left_store():
                new_customers_in_store.append(customer)
        self.customers_in_store = new_customers_in_store
        # add customer data to history
        self.history.add_customer_data(
            len(self.customers_in_store),
            self.n_customers_who_visited,
            self.n_newly_infected,
            self.n_infected_who_visited
        )

    def __get_next_customer(self) -> Optional[Customer]:
        """Determine if a new customer will join the queue this tick and return them if so"""
        # check if there are any remaining customers
        if self.n_customers_who_visited >= self.n_customers:
            return None
        # calculate the probability of a new customer arriving at this time
        x = self.config['customers']['arrival_gamma'] * (self.cur_tick / self.total_ticks)
        arrival_prob = (gamma.pdf(x, a=3.5, scale=4.5) * 3) + (gamma.pdf(x, a=18, scale=2) * 4)
        arrival_prob *= self.config['customers']['arrival_prob_scale']
        # check if the customer will join and return them if so
        if random.uniform(0, 1) <= arrival_prob:
            return self.customers[self.n_customers_who_visited]
        return None


if __name__ == '__main__':
    simulation = Simulation()
    simulation.run_n_simulations(3)
