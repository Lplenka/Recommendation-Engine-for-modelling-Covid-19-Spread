import random
import time

from config import get_full_config
from customer import Customer
from path_generator import generate_path_for_customer
from store_layouts import get_store_graph
from visualise import Visualiser


class Simulation:
    def __init__(self, config):
        self.config = get_full_config(config)
        self.__set_random_seed()
        self.store_graph = get_store_graph(self.config)
        
    def __set_random_seed(self):
        """Sets the random seed to make simulations repeatable"""
        if self.config['seed'] is None:
            self.config['seed'] = str(time.time())
        random.seed(self.config['seed'])

    def test_path_generation(self):
        """Temporary method for testing basic path generation"""
        customer = Customer(self.config)
        while len(customer.will_visit) == 0:
            customer = Customer(self.config)
        path = generate_path_for_customer(customer, self.store_graph)
        visualiser = Visualiser(self.config, self.store_graph, path)
        visualiser.run()


if __name__ == '__main__':
    sim = Simulation({})
    sim.test_path_generation()
