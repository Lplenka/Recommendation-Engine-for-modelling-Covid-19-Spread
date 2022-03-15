import random


class Customer:
    def __init__(self, config) -> None:
        num_sections = config['num_sections']
        num_shelves = config['num_shelves_per_aisle']
        percent_visit_section = config['percent_visit_section']
        self.will_visit = []
        for section in range(num_sections):
            if random.uniform(0, 1) < percent_visit_section[section]:
                shelf = random.randint(0, num_shelves - 1)
                self.will_visit.append((section, shelf))
