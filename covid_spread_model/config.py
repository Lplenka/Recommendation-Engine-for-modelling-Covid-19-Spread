DEFAULT = {
    # randomness
    'seed': None,
    # store
    'num_sections': 8,
    'num_aisles_horizontal': 4,
    'num_aisles_vertical': 2,
    'num_shelves_per_aisle': 4,
    'percent_visit_section': [
        0.48, 0.27, 0.62, 0.38, 0.22, 0.18, 0.53, 0.24
    ],
}


def get_full_config(config):
    """Merges the default and user-defined configs"""
    return merge_dicts_recursive(config, DEFAULT)


def merge_dicts_recursive(custom, default):
    """Merges two dictionaries recursively"""
    for key, value in default.items():
        if key not in custom:
            custom[key] = value
        elif type(value) == dict:
            custom[key] = merge_dicts_recursive(custom[key], value)
    return custom
