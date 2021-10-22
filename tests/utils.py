from typing import Optional


def get_specific_dict_item(dict_list: list, k_v_pair: tuple) -> Optional[dict]:
    k, v = k_v_pair
    return next((item for item in dict_list if item[k] == v), None)
