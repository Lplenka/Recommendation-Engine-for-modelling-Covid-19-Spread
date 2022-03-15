import networkx as nx


def get_store_graph(config):
    """
        Returns a simple store graph with entrance (S), exit (E), 8 sections and no checkout

        ##############
        ##          ##
        #1 13 35 57 7#
        #1 13 35 57 7#
        #1 13 35 57 7#
        #1 13 35 57 7#
        ##          ##
        #0 02 24 46 6#
        #0 02 24 46 6#
        #0 02 24 46 6#
        #0 02 24 46 6#
        ##          ##
        ##S########E##
    """
    # read config values
    num_aisles_hor = config['num_aisles_horizontal']
    num_aisles_ver = config['num_aisles_vertical']
    shelves_per_aisle = config['num_shelves_per_aisle']
    # additional calculated values
    num_nodes_hor = num_aisles_hor
    num_nodes_ver = 1 + (num_aisles_ver * (shelves_per_aisle + 1))
    num_nodes = 2 + (num_nodes_hor * num_nodes_ver)
    start_node = num_nodes - 2
    end_node = num_nodes - 1
    # helper lambda functions
    coord_to_node = lambda x, y: (x * num_nodes_ver) + y
    is_aisle = lambda y: y % (shelves_per_aisle + 1) > 0
    # init graph and add nodes
    graph = nx.Graph()
    for n in range(num_nodes):
        graph.add_node(n)
    # add all edges except entrance and exit ones
    for x in range(num_nodes_hor):
        for y in range(num_nodes_ver):
            n = coord_to_node(x, y)
            if not is_aisle(y) and x < num_nodes_hor - 1:
                graph.add_edge(n, coord_to_node(x + 1, y))
            if y < num_nodes_ver - 1:
                graph.add_edge(n, coord_to_node(x, y + 1))
    # add entrance and exit edges
    graph.add_edge(start_node, coord_to_node(0, 0))
    graph.add_edge(end_node, coord_to_node(num_nodes_hor - 1, 0))
    # calculate shortest paths between all pairs of nodes
    all_paths = {}
    for s in range(num_nodes):
        for e in range(s + 1, num_nodes):
            all_paths[(s, e)] = nx.shortest_path(graph, s, e)
    # return the graph and related information
    return {
        'graph': graph,
        'paths': all_paths,
        'start_node': start_node,
        'end_node': end_node
    }
