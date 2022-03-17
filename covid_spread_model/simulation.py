import random
import time

from config import get_full_config
from customer import Customer
from store import Store
from store_path import StorePath
from visualizer import Visualizer


class Simulation:
    def __init__(self, config: dict) -> None:
        """Initialises the simulation"""
        self.config = get_full_config(config)
        self.__set_random_seed()
        self.store = Store(self.config)
        
    def __set_random_seed(self) -> None:
        """Sets the random seed to make simulations repeatable"""
        if self.config['seed'] is None:
            self.config['seed'] = str(time.time())
        random.seed(self.config['seed'])

    def test_path_generation(self) -> None:
        """Temporary method for testing path generation and visualization"""
        customer = Customer(self.config)
        store_path = StorePath(customer, self.store)
        visualizer = Visualizer(self.config, self.store)
        visualizer.add_path(store_path)
        visualizer.run()


if __name__ == '__main__':
    sim = Simulation({})
    sim.test_path_generation()
