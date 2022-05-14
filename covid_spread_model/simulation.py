import math
import matplotlib.pyplot as plt
import numpy as np
import random
from csv import reader
from scipy.stats import gamma
from typing import List, Optional, Set, Tuple

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
            if not customer.has_left_store():
                customer.shopping_time += 1
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
            else:
                self.history.add_individual_customer_data(
                    customer.exposure_time,
                    customer.shopping_time,
                    customer.infection_duration > 0
                )
        self.customers_in_store = new_customers_in_store
        # add customer data to history
        self.history.add_overall_customer_data(
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
    
    def print_basic_results(self) -> None:
        """Very messy results calculations"""
        tick_dur = self.config['flow']['tick_duration_sec']
        # init empty arrays
        n_cust, n_cust_i, n_cust_s = [], [], []
        n_cust_store, shop_time = [], []
        et_tot, et_sus, et_inf = [], [], []
        pct_sus_exp = []
        n_new_inf, chance_inf_sus = [], []
        # populate arrays
        for i in range(self.history.n_simulations):
            # num customers
            n_cust.append(self.history.n_customers_who_visited[i][-1])
            n_cust_i.append(self.history.n_infected_who_visited[i][-1])
            n_cust_s.append(n_cust[-1] - n_cust_i[-1])
            n_cust_store.append(np.mean(np.array(self.history.n_customers_in_store[i])))
            # shopping
            shop_time.append(tick_dur * np.mean(np.array(self.history.customer_shopping_times[i])))
            # exposure
            et_tot.append(tick_dur * sum(map(lambda t: t[0], self.history.customer_exposure_times[i])))
            et_sus_lst = [t[0] for t in self.history.customer_exposure_times[i] if not t[1]]
            et_inf_lst = [t[0] for t in self.history.customer_exposure_times[i] if t[1]]
            et_sus.append(tick_dur * sum(et_sus_lst) / len(et_sus_lst))
            et_inf.append(tick_dur * sum(et_inf_lst) / len(et_inf_lst))
            pct_sus_exp.append(sum(1 for t in et_sus_lst if t > 0) / len(et_sus_lst))
            n_new_inf.append(self.history.n_newly_infected[i][-1])
            chance_inf_sus.append(n_new_inf[-1] / n_cust_s[-1])
        # list metrics and relevant arrays
        result_arrs = [
            ['num daily customers', n_cust, 2],
            ['num infected customers', n_cust_i, 2],
            ['num susceptible customers', n_cust_s, 2],
            ['mean num in store', n_cust_store, 2],
            ['mean shop time (sec)', shop_time, 2],
            ['total exp time (sec)', et_tot, 2],
            ['mean exp time (sec) per susceptible cust', et_sus, 2],
            ['total exp time (sec) per infected cust', et_inf, 2],
            ['proportion of susceptible cust with any exposure', pct_sus_exp, 4],
            ['num new infections', n_new_inf, 2],
            ['proportion of infections per susceptible cust', chance_inf_sus, 5],
        ]
        # calculate results and print
        print('metric,mean,sd')
        for metric, arr, rnd in result_arrs:
            arr = np.array(arr)
            print(f'{metric},{round(np.mean(arr), rnd)},{round(np.std(arr), rnd)}')

    def plot_basic_results(self) -> None:
        """Plots a selection of basic results"""
        self.__plot_customers_in_store()
        self.__hist_customers_newly_infected()
        self.__plot_customers_newly_infected()
        self.__plot_customer_exposure_time()
        self.__hist_customer_infection_chance()
    
    def __plot_customers_in_store(self) -> None:
        """Plots the average number of customers in the store at each tick"""
        X = np.array(range(self.total_ticks))
        Y, sd = self.__get_average_history_array(self.history.n_customers_in_store, self.total_ticks)
        # only show every 20th element to make the curve smoother
        X, Y, sd = X[::20], Y[::20], sd[::20]
        ticks, labels = self.__get_time_ticks()
        plt.plot(X, Y, color='royalblue')
        plt.fill_between(X, Y - sd, Y + sd, color='lightsteelblue')
        plt.xticks(ticks=ticks, labels=labels, rotation=45)
        plt.xlabel('Time')
        plt.ylabel('Mean number of customers in store')
        plt.show()

    def __hist_customers_newly_infected(self) -> None:
        """Plots a histogram of the number of newly infected customers from each sim"""
        X = [
            self.history.n_newly_infected[i][-1]
            for i in range(self.history.n_simulations)
        ]
        plt.hist(X, bins=20, color='cornflowerblue')
        plt.xlim([0, 100])
        plt.xlabel('Number of new infections')
        plt.ylabel('Number of simulations')
        plt.show()
    
    def __plot_customers_newly_infected(self) -> None:
        """Plots the average number of newly infected customers
            and total infected that customers visited at each tick"""
        X = np.array(range(self.total_ticks))
        Y1, sd1 = self.__get_average_history_array(self.history.n_newly_infected, self.total_ticks)
        Y2, sd2 = self.__get_average_history_array(self.history.n_infected_who_visited, self.total_ticks)
        ticks, labels = self.__get_time_ticks()
        plt.plot(X, Y1, color='royalblue', label='Newly infected')
        plt.plot(X, Y2, color='orange', label='Previously infected')
        plt.fill_between(X, Y1 - sd1, Y1 + sd1, color='lightsteelblue', alpha=0.5)
        plt.fill_between(X, Y2 - sd2, Y2 + sd2, color='moccasin', alpha=0.5)
        plt.xticks(ticks=ticks, labels=labels, rotation=45)
        plt.xlabel('Time')
        plt.ylabel('Mean number of customers')
        plt.legend()
        plt.show()

    def __plot_customer_exposure_time(self) -> None:
        """This method could be drastically improved but it works for now"""
        tick_duration_sec = self.config['flow']['tick_duration_sec']
        exp_times_sec = []
        for i in range(self.history.n_simulations):
            cust_exp_times = self.history.customer_exposure_times[i]
            for j in range(len(cust_exp_times)):
                exp_times_sec.append(tick_duration_sec * cust_exp_times[j][0])
        n_bins = int(math.ceil(max(exp_times_sec) // tick_duration_sec)) + 1
        X = [i * tick_duration_sec for i in range(n_bins)]
        Y = [0] * n_bins
        for t in exp_times_sec:
            Y[t // tick_duration_sec] += 1
        for i in range(n_bins):
            Y[i] /= len(exp_times_sec)
        plt.plot(X, Y, color='royalblue')
        plt.xlabel('Exposure time (s)')
        plt.ylabel('Proportion of customers')
        plt.xlim([-3, 35])
        plt.ylim([0, 1])
        plt.show()
    
    def __hist_customer_infection_chance(self) -> None:
        inf_chances = []
        for i in range(self.history.n_simulations):
            final_n_vis = self.history.n_customers_who_visited[i][-1]
            final_n_inf = self.history.n_infected_who_visited[i][-1]
            final_n_new = self.history.n_newly_infected[i][-1]
            inf_chance = final_n_new / (final_n_vis - final_n_inf)
            inf_chances.append(100 * inf_chance)
        plt.hist(inf_chances, color='cornflowerblue')
        plt.xlabel('Susceptible customer infection chance (%)')
        plt.ylabel('Number of simulations')
        plt.show()

    def __get_average_history_array(self, history_array: List[List[int]], length: int) -> Tuple[List[float], List[float]]:
        """Gets the mean values of a history array over all simulations"""
        avg_arr = [0] * length
        std_arr = [0] * length
        for i in range(length):
            for j in range(self.history.n_simulations):
                avg_arr[i] += history_array[j][i]
            avg_arr[i] /= self.history.n_simulations
            for j in range(self.history.n_simulations):
                std_arr[i] += (avg_arr[i] - history_array[j][i]) ** 2
            std_arr[i] = (std_arr[i] / self.history.n_simulations) ** 0.5
        return np.array(avg_arr), np.array(std_arr)
    
    def __get_time_ticks(self) -> Tuple[List[int], List[str]]:
        opening_time = self.config['flow']['opening_time']
        hours_open = self.config['flow']['hours_open']
        ticks_per_hour = 3600 // self.config['flow']['tick_duration_sec']
        hours = list(range(opening_time, opening_time + hours_open + 1))
        ticks = [i * ticks_per_hour for i in range(hours_open + 1)]
        labels = [str(hour).zfill(2) + ':00' for hour in hours]
        return ticks, labels


if __name__ == '__main__':
    import pickle
    simulation = Simulation()
    #simulation.run_n_simulations(100)
    #with open('history.pkl', 'wb') as f:
        #pickle.dump(simulation.history, f)
    with open('history.pkl', 'rb') as f:
        simulation.history = pickle.load(f)
    simulation.print_basic_results()
    simulation.plot_basic_results()
