from shop_elem import ShopElem
from collections import defaultdict
import numpy as np


class ShopParser:
    def __init__(self):
        self.map = None
        self.elements = defaultdict(list)

    def parse(self, numeric_map):
        # Transpose and flip 180 to mach mesa grid orientation
        self.map = np.transpose(numeric_map)
        self.map = np.flip(self.map, 0)
        self.map = np.array([[ShopElem(e) for e in row] for row in self.map])

        for coord, elem in np.ndenumerate(self.map):
            elem = self.map[coord]
            self.elements[elem].append(coord)

        self.elements[ShopElem.SHELF] = [(s, self.get_access_place(s)) for s in self.elements[ShopElem.SHELF]]

    def get_access_place(self, shelf):
        x, y = shelf

        # Right
        if x > 0 and self.map[x - 1, y] == ShopElem.SHOPPING_AREA:
            return x - 1, y
        # Left
        elif x < self.map.shape[0] - 1 and self.map[x + 1, y] == ShopElem.SHOPPING_AREA:
            return x + 1, y
        # Top
        elif self.map[x, y + 1] == ShopElem.SHOPPING_AREA:
            return x, y + 1


