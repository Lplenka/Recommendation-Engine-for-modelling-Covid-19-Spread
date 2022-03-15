from itertools import permutations


def generate_path_for_customer(customer, store_graph):
    """Generates an optimal path through the graph for a specific customer"""
    start_node = store_graph['start_node']
    end_node = store_graph['end_node']
    visit_nodes = []
    for section, shelf in customer.will_visit:
        visit_nodes.append(section_shelf_to_node(section, shelf))
    min_dist = 1e10
    min_nodes = []
    for permutation in permutations(visit_nodes):
        dist = get_dist_between_nodes(store_graph, start_node, permutation[0])
        for i in range(len(permutation) - 1):
            dist += get_dist_between_nodes(store_graph, permutation[i], permutation[i + 1])
        dist += get_dist_between_nodes(store_graph, permutation[-1], end_node)
        if dist < min_dist:
            min_dist = dist
            min_nodes = [start_node] + list(permutation) + [end_node]
    path = [start_node]
    for i in range(len(min_nodes) - 1):
        path.extend(get_path_between_nodes(store_graph, min_nodes[i], min_nodes[i + 1])[1:])
    return {
        'nodes': min_nodes,
        'path': path
    }


def section_shelf_to_node(section, shelf):
    """This is only hard-coded for testing - it should be dynamically calculated"""
    section_roots = {
        0: 1, 1: 6, 2: 12, 3: 17,
        4: 23, 5: 28, 6: 34, 7: 39
    }
    return section_roots[section] + shelf


def get_dist_between_nodes(store_graph, start, end):
    """Gets the distance between two nodes"""
    return len(get_path_between_nodes(store_graph, start, end))


def get_path_between_nodes(store_graph, start, end):
    """Gets the path between two nodes"""
    return store_graph['paths'][(start, end)]
