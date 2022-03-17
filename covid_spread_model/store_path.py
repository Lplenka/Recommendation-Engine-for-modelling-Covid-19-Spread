from copy import deepcopy
from itertools import permutations

from customer import Customer
from store import Store


class StorePath:
    def __init__(self, customer: Customer, store: Store) -> None:
        """Constructs the optimal path through the store for the given customer"""
        self.customer = customer
        self.store = store
        self.__generate_path()
    
    def __generate_path(self) -> None:
        """Finds the path with min distance through the store (brute-force travelling salesman)"""
        # convert store locations to nodes
        nodes_visits = list(
            self.store.location_to_node(*location)
            for location in self.customer.visits
        )
        # find order of nodes that has the smallest travel distance
        best_dist = 1e10
        best_nodes = []
        for permutation in permutations(nodes_visits):
            nodes = [self.store.node_start] + list(permutation) + [self.store.node_end]
            dist = sum(
                self.store.get_nodes_dist(nodes[i], nodes[i + 1])
                for i in range(len(nodes) - 1)
            )
            if dist < best_dist:
                best_dist = dist
                best_nodes = deepcopy(nodes)
        # construct the full path from the best nodes
        best_path = [self.store.node_start]
        for i in range(len(best_nodes) - 1):
            best_path.extend(self.store.get_nodes_path(best_nodes[i], best_nodes[i + 1])[1:])
        # store the nodes and path
        self.nodes_visit = best_nodes
        self.nodes_path = best_path