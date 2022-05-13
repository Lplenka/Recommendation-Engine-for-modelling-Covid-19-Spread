import random
from typing import List, Tuple

from store import Store


class StorePath:
    def __init__(self, visits: List[int], store: Store, config: dict) -> None:
        """Constructs the optimal path through the store for the given customer visits"""
        self.visits = visits
        self.store = store
        self.nodes_visit, self.nodes_path, self.wait_times = self.__generate_path(config)

    def __generate_path(self, config: dict) -> Tuple[List[int], List[int], List[int]]:
        """Finds optimal path through the store (nearest neighbour travelling salesman)"""
        nodes_visits = list(
            self.store.location_to_node(*location)
            for location in self.visits
        )
        # init best nodes and path
        cur_node = self.store.node_start
        best_nodes = [cur_node]
        best_path = [cur_node]
        # init node wait times
        wait_times = []
        wait_times.append(1) # start node has 1 wait time
        # if all the nodes have been visited, then terminate
        while len(nodes_visits):
            # find the shortest edge connecting the current node to an unvisited node
            best_node = None
            best_dist = 1e10
            for node in nodes_visits:
                dist = self.store.get_nodes_dist(cur_node, node)
                if dist < best_dist:
                    best_dist = dist
                    best_node = node
            best_nodes.append(best_node)
            this_path = self.store.get_nodes_path(cur_node, best_node)[1:]
            best_path.extend(this_path)
            # update wait times
            wait_times.extend([0] * (len(this_path) - 1)) # intermediate nodes have no wait time
            wait_time = random.randint(*config['customers']['item_wait_range'])
            # if we're at the same section twice in a row just increment the previous wait time
            if len(this_path):
                wait_times.append(wait_time)
            else:
                wait_times[-1] += wait_time
            # set next_node as cur_node, mark next_node as visited.
            cur_node = best_node
            nodes_visits.remove(cur_node)
        # add till and exit nodes and paths
        till_path = self.store.get_nodes_path(best_nodes[-1], self.store.node_till)[1:]
        best_path.extend(till_path)
        exit_path = self.store.get_nodes_path(self.store.node_till, self.store.node_end)[1:]
        best_path.extend(exit_path)
        best_nodes.extend([self.store.node_till, self.store.node_end])
        # update wait times
        wait_times.extend([0] * (len(till_path) - 1)) # intermediate nodes have no wait time
        wait_times.append(random.randint(*config['customers']['till_wait_range']))
        wait_times.extend([0] * len(exit_path)) # intermediate and exit nodes have no wait time
        # return the final nodes, path and wait times
        return best_nodes, best_path, wait_times
