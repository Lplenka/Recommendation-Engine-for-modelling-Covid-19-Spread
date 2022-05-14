from store import Store


class History:
    def __init__(self, n_simulations: int, store: Store, total_ticks: int) -> None:
        """Stores the results of the simulations"""
        self.n_simulations = n_simulations
        self.store = store
        self.total_ticks = total_ticks
        self.cur_simulation = 0
        self.cur_tick = 0
        # prepare data structures
        self.node_exposure_times = []
        self.n_customers_in_store = []
        self.n_customers_who_visited = []
        self.n_newly_infected = []
        self.n_infected_who_visited = []
        self.customer_exposure_times = []
        self.customer_shopping_times = []
        for _ in range(self.n_simulations):
            self.node_exposure_times.append([0] * self.store.n_nodes)
            self.n_customers_in_store.append([0] * self.total_ticks)
            self.n_customers_who_visited.append([0] * self.total_ticks)
            self.n_newly_infected.append([0] * self.total_ticks)
            self.n_infected_who_visited.append([0] * self.total_ticks)
            self.customer_exposure_times.append([])
            self.customer_shopping_times.append([])
    
    def next_simulation(self) -> None:
        """Move on to the next simulation"""
        self.cur_simulation += 1
        self.cur_tick = 0

    def next_tick(self) -> None:
        """Move on to the next tick"""
        self.cur_tick += 1

    def add_exposure_time(self, node: int) -> None:
        """Adds a tick of exposure time to this node during this simulation"""
        self.node_exposure_times[self.cur_simulation][node] += 1

    def add_overall_customer_data(self, n_customers_in_store: int, n_customers_who_visited: int,
        n_newly_infected: int, n_infected_who_visited: int) -> None:
        """Stores multiple customer-related values for this simulation and tick"""
        self.n_customers_in_store[self.cur_simulation][self.cur_tick] = n_customers_in_store
        self.n_customers_who_visited[self.cur_simulation][self.cur_tick] = n_customers_who_visited
        self.n_newly_infected[self.cur_simulation][self.cur_tick] = n_newly_infected
        self.n_infected_who_visited[self.cur_simulation][self.cur_tick] = n_infected_who_visited

    def add_individual_customer_data(self, exposure_time: int, shopping_time: int, was_infected: bool) -> None:
        """Stores multiple individual customer values for this simulation"""
        self.customer_exposure_times[self.cur_simulation].append((exposure_time, was_infected))
        self.customer_shopping_times[self.cur_simulation].append(shopping_time)
