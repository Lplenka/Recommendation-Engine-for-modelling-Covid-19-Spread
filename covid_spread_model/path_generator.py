from copy import deepcopy
from itertools import permutations


def generate_path_for_customer(customer, store_graph):
    start_node = store_graph['start_node']
    end_node = store_graph['end_node']
    visit_nodes = []
    for section, shelf in customer.will_visit:
        visit_nodes.append(section_shelf_to_node(section, shelf))
    min_path = []
    min_dist = 1e10
    for permutation in permutations(visit_nodes):
        cur_dist, cur_path = get_path_between_nodes(store_graph, start_node, permutation[0])
        for i in range(len(visit_nodes) - 1):
            next_dist, next_path = get_path_between_nodes(store_graph, visit_nodes[i], visit_nodes[i + 1])
            cur_dist += next_dist
            cur_path.extend(next_path)
        next_dist, next_path = get_path_between_nodes(store_graph, permutation[-1], end_node)
        cur_dist += next_dist
        cur_path.extend(next_path)
        if cur_dist < min_dist:
            min_dist = cur_dist
            min_path = deepcopy(cur_path)
    return min_path


def section_shelf_to_node(section, shelf):
    """This is only hard-coded for testing - it should be dynamically calculated"""
    roots = {
        0: (0, 1), 1: (0, 6),
        2: (1, 1), 3: (1, 6),
        4: (2, 1), 5: (2, 6),
        6: (3, 1), 7: (3, 6),
    }
    x, y = roots[section]
    return (x * 2) + y + shelf


def get_path_between_nodes(store_graph, start, end):
    """Gets the distance and path between two nodes"""
    if start == end:
        return 0, []
    if end < start:
        start, end = end, start
    path = store_graph['paths'][(start, end)]
    return len(path), path
