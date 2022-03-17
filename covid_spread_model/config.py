DEFAULT_CONFIG = {
    # randomness
    'seed': None,
    # store
    'store': {
        'n_sections': 8,
        'n_aisles_w': 4,
        'n_aisles_h': 2,
        'n_shelves': 4,
        'pc_visit_sections': [
            0.48, 0.27, 0.62, 0.38, 0.22, 0.18, 0.53, 0.24
        ],
        'pc_visit_shelves': [
            [0.25, 0.25, 0.25, 0.25],
            [0.25, 0.25, 0.25, 0.25],
            [0.25, 0.25, 0.25, 0.25],
            [0.25, 0.25, 0.25, 0.25],
            [0.25, 0.25, 0.25, 0.25],
            [0.25, 0.25, 0.25, 0.25],
            [0.25, 0.25, 0.25, 0.25],
            [0.25, 0.25, 0.25, 0.25],
        ],
    },
    # visualizer
    'visualizer': {
        'pixels_per_unit': 50,
    },
}


def get_full_config(config: dict) -> dict:
    """Merges the default and user-defined configs"""
    return merge_configs_recursive(config, DEFAULT_CONFIG)


def merge_configs_recursive(config: dict, default: dict) -> dict:
    """Merges config dictionaries recursively"""
    for key, value in default.items():
        if key not in config:
            config[key] = value
        elif type(value) == dict:
            config[key] = merge_configs_recursive(config[key], value)
    return config
