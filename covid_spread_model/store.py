import networkx as nx
from typing import List


class Store:
    def __init__(self, config: dict) -> None:
        """Constructs a store graph and finds paths between its nodes"""
        # read config values
        self.n_sections = config['store']['n_sections']
        self.n_aisles_w = config['store']['n_aisles_w']
        self.n_aisles_h = config['store']['n_aisles_h']
        self.n_shelves = config['store']['n_shelves']
        # calc some other values
        self.n_nodes_w = self.n_aisles_w
        self.n_nodes_h = 1 + (self.n_aisles_h * (self.n_shelves + 1))
        self.n_nodes = 3 + (self.n_nodes_w * self.n_nodes_h)
        self.node_till = self.n_nodes - 3
        self.node_start = self.n_nodes - 2
        self.node_end = self.n_nodes - 1
        # get graph and paths
        self.graph = self.__construct_graph()
        self.paths = self.__construct_paths()
    
    def __construct_graph(self) -> nx.Graph:
        """Constructs a NetworkX graph of the store"""
        # init graph with nodes
        graph = nx.Graph()
        for n in range(self.n_nodes):
            graph.add_node(n)
        # add all edges except till/entrance/exit edges
        for x in range(self.n_nodes_w):
            for y in range(self.n_nodes_h):
                n = self.coord_to_node(x, y)
                # move right if not in an aisle and there's space
                if not self.coord_is_aisle(x, y) and x < self.n_nodes_w - 1:
                    graph.add_edge(n, self.coord_to_node(x + 1, y))
                # move up if there's space
                if y < self.n_nodes_h - 1:
                    graph.add_edge(n, self.coord_to_node(x, y + 1))
        # add till/entrance/exit edges and return
        graph.add_edge(self.node_till, self.coord_to_node(self.n_nodes_w - 2, 0))
        graph.add_edge(self.node_start, self.coord_to_node(0, 0))
        graph.add_edge(self.node_end, self.coord_to_node(self.n_nodes_w - 1, 0))
        return graph
    
    def __construct_paths(self) -> dict:
        """Finds the shortest paths between every pair of nodes in the graph"""
        paths = {}
        for n0 in range(self.n_nodes):
            for n1 in range(self.n_nodes):
                paths[(n0, n1)] = nx.shortest_path(self.graph, n0, n1)
        return paths

    def coord_to_node(self, x: int, y: int) -> int:
        """Gets the node number of an (x, y) coordinate"""
        return (x * self.n_nodes_h) + y
    
    def coord_is_aisle(self, x: int, y: int) -> bool:
        """Checks whether an (x, y) coordinate is in an aisle"""
        return y % (self.n_shelves + 1) > 0
    
    def location_to_node(self, section: int, shelf: int) -> int:
        """Gets the node number of a particular shelf in a store section"""
        section_x = section // self.n_aisles_h
        section_y = section % self.n_aisles_h
        section_root = (section_x * self.n_nodes_h) + (1 + (section_y * (self.n_shelves + 1)))
        return section_root + shelf
    
    def get_nodes_dist(self, n0: int, n1: int) -> int:
        """Gets the distance between two nodes"""
        return len(self.get_nodes_path(n0, n1))

    def get_nodes_path(self, n0: int, n1: int) -> List[int]:
        """Gets the path between two nodes"""
        return self.paths[(n0, n1)]
