import os
import json
from .utils import get_path
from typing import Dict, Any


def get_data_from_file() -> Dict[str, Any]:
    path = get_path('data')
    persistent_data: Dict[str, Any] = {'chat_ids': [], "image_index": 0}

    if os.path.isfile(path):
        with open(path, 'r') as file:
            persistent_data = json.load(file)

    return persistent_data


def save_data_to_file(data: Dict[str, Any]):
    path = get_path('data')

    with open(path, 'w') as file:
        json.dump(data, file)
