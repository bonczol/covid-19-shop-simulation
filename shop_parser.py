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


