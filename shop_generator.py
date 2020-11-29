import numpy as np
import itertools
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from shop_elem import ShopElem


class ShopGenerator:
    def __init__(self, rows, shelves_in_row, shelf_length, space_between_rows, space_between_shelves, checkout_height=5,
                 checkouts_num=4):
        self.rows = rows
        self.shelves_in_row = shelves_in_row
        self.shelf_length = shelf_length
        self.space_between_rows = space_between_rows
        self.space_between_shelves = space_between_shelves
        self.checkout_height = checkout_height
        self.checkouts_num = checkouts_num

        self.double_shelf_width = 2
        self.checkout_width = 1
        self.door_size = 2

        self.map_ = None
        self._draw_shop_map()

    def plot(self):
        plt.matshow(self.map_, cmap=ListedColormap(['white', 'yellow', 'grey', 'black', 'pink', 'green', 'red']))
        plt.xticks(np.arange(0, self.map_.shape[1]))
        plt.yticks(np.arange(0, self.map_.shape[0]))
        plt.gca().set_xticks([x - 0.5 for x in plt.gca().get_xticks()][1:], minor='true')
        plt.gca().set_yticks([y - 0.5 for y in plt.gca().get_yticks()][1:], minor='true')
        plt.grid(which='minor')

    def save(self, filename):
        np.savetxt(filename, self.map_, fmt='%s')

    def _draw_shop_map(self):
        self._draw_shop_center()
        self._draw_shop_borders()
        self._draw_shop_checkouts()
        self._draw_walls()
        self._draw_entry_and_exit()
        self.plot()

    def _draw_shop_center(self):
        # Calculate height/width to fill space with given number of shelves
        height = self.rows * self.shelf_length + (self.rows - 1) * self.space_between_rows
        width = self.shelves_in_row * self.double_shelf_width + ((self.shelves_in_row - 1) * self.space_between_shelves)

        self.map_ = np.full((height, width), ShopElem.SHOPPING_AREA.value)

        # Find (x,y) of top-left shelf's corner
        aisles_x = np.arange(height, step=self.shelf_length + self.space_between_rows)
        aisles_y = np.arange(width, step=self.space_between_shelves + self.double_shelf_width)

        for x, y in itertools.product(aisles_x, aisles_y):
            self.map_[x:x + self.shelf_length, y:y + self.double_shelf_width] = ShopElem.SHELF.value

    def _draw_shop_borders(self):
        # Shelves on left and right side
        side_shelf = np.full((self.map_.shape[0], 1), ShopElem.SHELF.value)
        side_blank_space = np.full((self.map_.shape[0], self.space_between_shelves), ShopElem.SHOPPING_AREA.value)
        self.map_ = np.hstack((side_shelf, side_blank_space, self.map_, side_blank_space, side_shelf))

        # Shelves on top and bottom side
        top_shelf = np.full((1, self.map_.shape[1]), ShopElem.SHELF.value)
        top_blank_space = np.full((self.space_between_shelves, self.map_.shape[1]), ShopElem.SHOPPING_AREA.value)

        bottom_blank_space = np.full((self.space_between_rows, self.map_.shape[1]), ShopElem.SHOPPING_AREA.value)
        bottom_blank_space[:, 0] = ShopElem.WALL.value

        # Corners
        top_shelf[:, 0:2] = ShopElem.WALL.value
        top_shelf[:, -2:] = ShopElem.WALL.value
        top_blank_space[:, 0] = ShopElem.WALL.value
        top_blank_space[:, -1] = ShopElem.WALL.value

        self.map_ = np.vstack((top_shelf, top_blank_space, self.map_, bottom_blank_space))

    def _draw_shop_checkouts(self):
        section_height = self.checkout_height + 2
        section = np.full((section_height, self.map_.shape[1]), ShopElem.EMPTY.value)

        # Checkouts
        checkouts_end = self.checkouts_num * 3

        for y in np.arange(checkouts_end, step=3):
            section[:self.checkout_height, y] = ShopElem.WALL.value
            section[self.checkout_height - 1, y] = ShopElem.CASHIER.value  # Put cashier in down-right corner
            section[:self.checkout_height, y + 2] = ShopElem.WALL.value

        # Separation between shop and checkout
        section[0, checkouts_end: -2] = ShopElem.WALL.value

        # Entrance corridor
        section[:, section.shape[1] - 2] = ShopElem.WALL.value

        # Add Entrance corridor to shopping area
        section[:, section.shape[1] - 1] = ShopElem.SHOPPING_AREA.value

        self.map_ = np.vstack((self.map_, section))

    def _draw_walls(self):
        side_wall = np.full((self.map_.shape[0], 1), ShopElem.WALL.value)
        self.map_ = np.hstack((side_wall, self.map_, side_wall))

        top_bottom_wall = np.full((1, self.map_.shape[1]), ShopElem.WALL.value)
        self.map_ = np.vstack((top_bottom_wall, self.map_, top_bottom_wall))

    def _draw_entry_and_exit(self):
        self.map_[-1, -2] = ShopElem.ENTRY.value
        self.map_[-1, -4] = ShopElem.EXIT.value
