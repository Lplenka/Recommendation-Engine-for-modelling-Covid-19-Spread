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
        self.customers = self.__generate_customers()

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
        for customer in self.customers:
            customer.reset_customer()
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

    def visualize_overlay(self) -> None:
        """Visualizes the store layout with nodes and edges overlayed"""
        visualizer = Visualizer(self.config, self.store)
        visualizer.add_node_overlay()
        visualizer.run()

    def visualize_path(self) -> None:
        """Visualizes a random customer's path through the store"""
        visualizer = Visualizer(self.config, self.store)
        visualizer.add_node_overlay()
        path = self.customers[random.randint(0, self.n_customers - 1)].path
        visualizer.add_path(path)
        visualizer.run()

    def visualize_exposure_time(self) -> None:
        """Visualizes the mean exposure time for each node as a heatmap"""
        visualizer = Visualizer(self.config, self.store)
        exposure_times = self.__get_average_history_array(
            self.history.node_exposure_times,
            self.store.n_nodes
        )
        # convert the exposure times from ticks to seconds
        exposure_times = list(map(
            lambda t: t * self.config['flow']['tick_duration_sec'],
            exposure_times
        ))
        visualizer.add_exposure_times(exposure_times)
        visualizer.run()
    
    def plot_basic_results(self) -> None:
        """Plots a selection of basic results"""
        self.__plot_customers_in_store()
        self.__plot_customers_newly_infected()
        self.__hist_customers_newly_infected()
    
    def __plot_customers_in_store(self) -> None:
        """Plots the average number of customers in the store at each tick"""
        X = list(range(self.total_ticks))
        Y = self.__get_average_history_array(self.history.n_customers_in_store, self.total_ticks)
        plt.plot(X, Y)
        plt.xlabel('Ticks')
        plt.ylabel('Mean number of customers in store')
        plt.show()
    
    def __plot_customers_newly_infected(self) -> None:
        """Plots the average number of newly infected customers
            and total infected that customers visited at each tick"""
        X = list(range(self.total_ticks))
        Y1 = self.__get_average_history_array(self.history.n_newly_infected, self.total_ticks)
        Y2 = self.__get_average_history_array(self.history.n_infected_who_visited, self.total_ticks)
        plt.plot(X, Y1, label='Newly infected')
        plt.plot(X, Y2, label='Previously infected')
        plt.xlabel('Ticks')
        plt.ylabel('Mean number of customers')
        plt.legend()
        plt.show()

    def __hist_customers_newly_infected(self) -> None:
        """Plots a histogram of the number of newly infected customers from each sim"""
        X = [
            self.history.n_newly_infected[i][-1]
            for i in range(self.history.n_simulations)
        ]
        n_bins = max(X) + 1
        plt.hist(X, bins=n_bins)
        plt.xlabel('Number of newly infected customers')
        plt.ylabel('Count')
        plt.show()

    def __get_average_history_array(self, history_array: List[List[int]], length: int) -> List[float]:
        """Gets the mean values of a history array over all simulations"""
        avg_arr = [0] * length
        for i in range(length):
            for j in range(self.history.n_simulations):
                avg_arr[i] += history_array[j][i]
            avg_arr[i] /= self.history.n_simulations
        return avg_arr


if __name__ == '__main__':
    simulation = Simulation()
    simulation.run_n_simulations(30)
    simulation.visualize_exposure_time()
    #simulation.plot_basic_results()
