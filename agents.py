import random

from mesa import Agent
from shop_elem import ShopElem
from scipy.stats import truncnorm
from helper import randint_normal
from helper import random_bool


class CustomerAgent(Agent):
    # TODO uzupenic braukjące parametry
    def __init__(self, unique_id, model, pos, sick, mask, risk_group):
        super().__init__(unique_id, model)
        self.pos = pos
        self.sick = sick
        self.mask = mask
        self.risk_group = risk_group
        self.shopping_list = self.get_shopping_list()

    def step(self):
        curr_shelf = self.shopping_list[0][0]

        for neighbor in self.model.grid.neighbor_iter(self.pos):
            # Infect another customer
            if self.sick and type(neighbor) == CustomerAgent and not neighbor.sick:
                if random_bool(self.get_infection_prob(neighbor)):
                    neighbor.get_sick()
            elif neighbor.pos == curr_shelf and type(neighbor) == ShelfAgent:
                # Infect shelf
                if self.sick:
                    if random_bool(self.model.infect_shelf_prob):
                        neighbor.get_sick()
                # Get infected by shelf
                else:
                    if random_bool(neighbor.get_infection_prob()):
                        self.get_sick()

        if self.shopping_list:
            self.move()
            if self.pos == self.shopping_list[0][1]:
                self.shopping_list.pop(0)
        else:
            self.go_to_out()

    def get_sick(self):
        self.sick = True
        self.model.infections += 1
        self.model.deaths += int(random_bool(self.model.death_ratio))

    def get_shopping_list(self):
        list_len = randint_normal(1, self.model.max_shopping_list, self.model.mean_shopping_list,
                                  self.model.std_dev_shopping_list)
        shopping_list = random.choices(self.model.shop.elements[ShopElem.SHELF], k=list_len)
        return shopping_list

    def move(self):
        a = self.find_path(self.shopping_list[0][1])
        print(a)
        if len(a) > 1:
            next_pos = a[-2]
        else:
            next_pos = a[0]

        if self.model.grid.is_cell_empty(next_pos):
            self.model.grid.move_agent(self, next_pos)

    def go_to_out(self):
        pos=self.pos
        if pos[1]==34:
            if self.model.grid.is_cell_empty((pos[0]-1, pos[1])):
                self.model.grid.move_agent(self, (pos[0]-1, pos[1]))
        elif pos[1]==33:
            if self.model.grid.is_cell_empty((pos[0], pos[1]+1)):
                self.model.grid.move_agent(self, (pos[0], pos[1]+1))
            elif self.model.grid.is_cell_empty((pos[0] + 1, pos[1])):
                self.model.grid.move_agent(self, (pos[0] + 1, pos[1]))
        elif pos[1]>26:
            if self.model.grid.is_cell_empty((pos[0], pos[1]+1)):
                self.model.grid.move_agent(self, (pos[0], pos[1]+1))
            elif self.model.grid.is_cell_empty((pos[0]+1, pos[1])):
                self.model.grid.move_agent(self, (pos[0]+1, pos[1]))
        else:
            next_pos = (pos[0], 27)
            if self.model.grid.is_cell_empty(next_pos):
                self.shopping_list.append((next_pos,next_pos))

    def get_grid(self):
        grid = []
        for i in self.model.grid.grid:
            a = []
            for j in i:
                if j is None:
                    a.append(0)
                else:
                    a.append(1)
            grid.append(a)
        return grid

    def find_path(self, end):
        m = []
        a = self.get_grid()
        for i in range(len(a)):
            m.append([])
            for j in range(len(a[i])):
                m[-1].append(0)
        i, j = self.pos
        m[i][j] = 1
        k = 0
        if a[end[0]][end[1]] != 0:
            return [(i, j)]
        while m[end[0]][end[1]] == 0 and k<50:
            k += 1
            self.make_step(m, a, k)
        i, j = end
        k = m[i][j]
        the_path = [(i, j)]
        while k > 1:
            if i > 0 and m[i - 1][j] == k - 1:
                i, j = i - 1, j
                the_path.append((i, j))
                k -= 1
            elif j > 0 and m[i][j - 1] == k - 1:
                i, j = i, j - 1
                the_path.append((i, j))
                k -= 1
            elif i < len(m) - 1 and m[i + 1][j] == k - 1:
                i, j = i + 1, j
                the_path.append((i, j))
                k -= 1
            elif j < len(m[i]) - 1 and m[i][j + 1] == k - 1:
                i, j = i, j + 1
                the_path.append((i, j))
                k -= 1
        return the_path


    def make_step(self, m, a, k):
        for i in range(len(m)):
            for j in range(len(m[i])):
                if m[i][j] == k:
                    if i > 0 and m[i - 1][j] == 0 and a[i - 1][j] == 0:
                        m[i - 1][j] = k + 1
                    if j > 0 and m[i][j - 1] == 0 and a[i][j - 1] == 0:
                        m[i][j - 1] = k + 1
                    if i < len(m) - 1 and m[i + 1][j] == 0 and a[i + 1][j] == 0:
                        m[i + 1][j] = k + 1
                    if j < len(m[i]) - 1 and m[i][j + 1] == 0 and a[i][j + 1] == 0:
                        m[i][j + 1] = k + 1

    def get_infection_prob(self, neighbour):
        if self.mask:
            if neighbour.mask:
                return self.model.carrier_mask_neighbour_mask
            else:
                return self.model.carrier_mask_neighbour_no_mask
        else:
            if neighbour.mask:
                return self.model.carrier_no_mask_neighbour_mask
            else:
                return self.model.carrier_no_mask_neighbour_no_mask

    def is_infected(self, neighbour):
        p = self.get_infection_prob(neighbour)
        return random_bool(p)


# TODO
class CashierAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos


class ShelfAgent(Agent):
    def __init__(self, unique_id, model, pos, sick_level):
        super().__init__(unique_id, model)
        self.pos = pos
        self.sick_level = sick_level

    def get_sick(self):
        if self.sick_level < 10:
            self.sick_level += 1

    def get_infection_prob(self):
        return (self.sick_level / self.model.max_shelf_sick_level) * self.model.touch_face_prob


class BackgroundAgent(Agent):
    def __init__(self, unique_id, model, pos, type_):
        super().__init__(unique_id, model)
        self.pos = pos
        self.type = type_


class TestAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
