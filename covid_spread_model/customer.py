import random
from typing import List, Tuple

Vector = List[float]
TupleInt = Tuple[int, int]


class Customer:
    def __init__(self, config: dict) -> None:
        """Constructs a customer with store locations to visit"""
        self.config = config
        self.visits = self.__get_visits()
        self.path = None
        self.infection_duration = 0
        self.infection_status = False
    
    def __get_visits(self) -> List[TupleInt]:
        """Generates a non-empty list of random store locations to visit"""
        pcv_sections = self.config['store']['pc_visit_sections']
        pcv_shelves = self.config['store']['pc_visit_shelves']
        visits = []
        for i, pcv_section in enumerate(pcv_sections):
            if random.uniform(0, 1) >= pcv_section: continue
            for j, pcv_shelf in enumerate(pcv_shelves[i]):
                if random.uniform(0, 1) >= pcv_shelf: continue
                visits.append((i, j))
        # if the customer isn't visiting any locations then regenerate the list
        if len(visits) == 0:
            visits = self.__get_visits()
        return visits

    def __get_visits_custom(self) -> List[TupleInt]:
        """Generates a non-empty list of random store locations to visit"""
        return []
    
    def __set_initial_infected_status(self) -> bool:
        """Determine the initial infection status for this customer"""
        return False
    
    def is_infected(self) -> bool:
        """Returns whether or not the customer is infected"""
        #set self.infection_duration (any number between 1 to 7)
        status = np.random.binomial(size=1, n=1, p=229.9/100000)
        if status[0] == 0:
            self.infection_status = False
            return False
        else:
            self.infection_status = True
            return True

    
    def update_visit_probabilities() -> None:
        """Updates item purchase probabilities based on most recent item purchases"""
        return

    def __init_position(self) -> None:
        """Initialises the customer's position"""
        return
    
    def update_position(self) -> None:
        """Updates the customer's position this tick"""
        return
    
    def get_position(self) -> TupleInt:
        """Returns the current position of the customer"""
        return (0, 0)
    
    def has_left_store(self) -> bool:
        """Returns whether or not the customer left the store this tick"""
        return False
    def calculate_transmissibility(self,R0,average_contacts,duration) -> float:  
        """Calculates the transmissibility or probability of transmission"""    
        return R0/(average_contacts*duration)

    def get_infection_duration(self) -> int:
        """Returns the duration for which the customer has been infected"""
        import random
        self.infection_duration = random.randint(1,7)
        return self.infection_duration

    def set_infection_duration(self,duration) -> None:
        """Sets the duration for which the customer has been infected(all customers infected in the simulation run would be given a value of 0)"""    
        self.infection_duration = duration
        return 
        
    def set_simulation_infection(self) -> None:
        self.infection_status = True
        return

    def update_infection_probability(self, other_customer: "Customer"):
        """Update this customer's infection prob. based on other customer's distance and infection status"""
        if self.is_infected() != other_customer.is_infected():
            if self.get_position() == other_customer.get_position():
                choices = [True,False]
                if (self.is_infected() and self.get_infection_duration() != 0 ):
                    transmissibility = self.calculate_transmissibility(2.5,3,self.get_infection_duration())
                    distribution = [transmissibility, 1 - transmissibility]
                    if random.choices(choices, distribution):
                        other_customer.set_simulation_infection()
                elif (other_customer.is_infected() and other_customer.get_infection_duration() != 0 ):
                    transmissibility = other_customer.calculate_transmissibility(2.5,3,other_customer.get_infection_duration())
                    distribution = [transmissibility, 1 - transmissibility]
                    if random.choices(choices, distribution):
                        self.set_simulation_infection()  
        return
