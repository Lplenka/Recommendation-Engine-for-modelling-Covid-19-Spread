DEFAULT_CONFIG = {
    # randomness
    'seed': None,
    # flow
    'tick_duration_sec': 5,
    # customers
    'customers': {
        'dataset_path': './dataset/aisle_vectors.csv',
    },
    # store
    'store': {
        'n_items': 134, # total items in dataset
        'items_per_section': 5, # combine each set of 5 items into a single section
        'n_sections': 27, # math.ceil(134 / 5)
        'n_aisles_w': 3, # 3 aisles wide
        'n_aisles_h': 3, # 3 aisles high --> 9 aisles total
        'n_shelves': 3, # 27 sections = 9 aisles * 3 shelves-per-aisle
    },
    # visualizer
    'visualizer': {
        'pixels_per_unit': 50,
    },
}


def get_full_config(config: dict) -> dict:
    """Merges the default and user-defined configs"""
    if config is None:
        return DEFAULT_CONFIG
    return merge_configs_recursive(config, DEFAULT_CONFIG)


def merge_configs_recursive(config: dict, default: dict) -> dict:
    """Merges config dictionaries recursively"""
    for key, value in default.items():
        if key not in config:
            config[key] = value
        elif type(value) == dict:
            config[key] = merge_configs_recursive(config[key], value)
    return config
