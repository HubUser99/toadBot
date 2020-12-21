import os
from typing import Literal


def get_path(path: Literal['images', 'data']):
    result = os.getenv('PATH_TO_IMAGES_DIRECTORY'
                       if path == 'images'
                       else 'PATH_TO_SAVE_FILE')
    if result == None:
        raise Exception("Environment variable not found")

    return result


def remove_item_from_list(list_to_use: list, item_to_remove: str):
    return list(filter(lambda item: item != item_to_remove, list_to_use))


def get_image_url(index: int):
    return 'https://raw.githubusercontent.com/jonshamir/frog-dataset/master/data-224/frog-' + str(index) + '.png'
