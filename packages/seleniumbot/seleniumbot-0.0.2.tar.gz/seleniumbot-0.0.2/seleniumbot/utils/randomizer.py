import random
from typing import Any, Callable


class Randomizer:

    @staticmethod
    def random_item_from_list(items: list[Any], comp: Callable, default: Any = None) -> Any:
        for item in items:
            x = random.randint(0, 1)
            if comp(item, x):
                return item

        return default

    @staticmethod
    def pick(objects: list) -> Any:
        return random.choice(objects)

    @staticmethod
    def between(x: int | float, y: int | float) -> int | float:
        if isinstance(x, float) or isinstance(y, float):
            return random.uniform(x, y)
        return random.randint(x, y)
