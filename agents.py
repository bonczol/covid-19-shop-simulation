import random

from mesa import Agent
from shop_elem import ShopElem
from scipy.stats import truncnorm
from helper import randint_normal
from helper import random_bool


class HumanAgent(Agent):
    def __init__(self, unique_id, model, pos, sick, mask, risk_group):
        super().__init__(unique_id, model)
        self.pos = pos
        self.sick = sick
        self.mask = mask
        self.risk_group = risk_group
        self.infected=sick

    def try_infect(self, neighbor):
        if random_bool(self.get_infection_prob(neighbor)):
            neighbor.get_sick()

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

    def get_sick(self):
        self.infected = True
        self.model.infections += 1
        death_prob = self.model.death_ratio_rg if self.risk_group else self.model.death_ratio
        self.model.deaths += int(random_bool(death_prob))


class CustomerAgent(HumanAgent):
    def __init__(self, unique_id, model, pos, sick, mask, risk_group):
        super().__init__(unique_id, model, pos, sick, mask, risk_group)
        self.shopping_list = self.get_shopping_list()

    def step(self):
        for neighbor in self.model.grid.neighbor_iter(self.pos):
            if self.sick and isinstance(neighbor, HumanAgent) and not neighbor.sick:
                neighbor.try_infect(neighbor)
            elif self.shopping_list and neighbor.pos == self.shopping_list[0][0] and type(neighbor) == ShelfAgent:
                if self.sick:
                    self.try_infect_shelf(neighbor)
                else:
                    neighbor.try_infect(self)

        if self.shopping_list:
            self.move()
            if self.pos == self.shopping_list[0][1]:
                self.shopping_list.pop(0)
        else:
            self.go_to_out()

    def try_infect_shelf(self, shelf):
        if random_bool(self.model.infect_shelf_prob):
            shelf.get_sick()

    def get_shopping_list(self):
        list_len = randint_normal(1, self.model.max_shopping_list, self.model.mean_shopping_list,
                                  self.model.std_dev_shopping_list)
        shopping_list = random.sample(self.model.shop.elements[ShopElem.SHELF], list_len)
        return shopping_list

    def move(self):
        a = self.find_path(self.shopping_list[0][1])
        if len(a) > 1:
            next_pos = a[-2]
        else:
            next_pos = a[0]

        if self.model.grid.is_cell_empty(next_pos):
            self.model.grid.move_agent(self, next_pos)

    def go_to_out(self):
        pos=self.pos
        if pos[1]==35:
            if self.model.grid.is_cell_empty((pos[0]-1, pos[1])):
                self.model.grid.move_agent(self, (pos[0]-1, pos[1]))
        elif pos[1]==34:
            if self.model.grid.is_cell_empty((pos[0], pos[1]+1)):
                self.model.grid.move_agent(self, (pos[0], pos[1]+1))
            elif self.model.grid.is_cell_empty((pos[0] + 1, pos[1])):
                self.model.grid.move_agent(self, (pos[0] + 1, pos[1]))
        elif pos[1]>27:
            if self.model.grid.is_cell_empty((pos[0], pos[1]+1)):
                self.model.grid.move_agent(self, (pos[0], pos[1]+1))
            elif self.model.grid.is_cell_empty((pos[0]+1, pos[1])):
                self.model.grid.move_agent(self, (pos[0]+1, pos[1]))
        else:
            next_pos = (pos[0], 28)
            if self.model.grid.is_cell_empty(next_pos):
                self.shopping_list.append((next_pos, next_pos))
            elif self.model.grid.is_cell_empty((pos[0]+1, pos[1])):
                self.shopping_list.append(((pos[0]+1, pos[1]), (pos[0]+1, pos[1])))

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
        while m[end[0]][end[1]] == 0:
            k += 1
            if k > 407: return [self.pos]
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


class CashierAgent(HumanAgent):
    def __init__(self, unique_id, model, pos, mask):
        super().__init__(unique_id, model, pos, False, mask, False)

    def step(self):
        for neighbor in self.model.grid.neighbor_iter(self.pos):
            if self.sick and type(neighbor) == CustomerAgent and not neighbor.sick:
                neighbor.try_infect(neighbor)


class ShelfAgent(Agent):
    def __init__(self, unique_id, model, pos, sick_level, desc_counter):
        super().__init__(unique_id, model)
        self.pos = pos
        self.sick_level = sick_level
        self.desc_counter = desc_counter

    def get_sick(self):
        if self.sick_level < 10:
            self.sick_level += 1

    def try_infect(self, neighbor):
        if random_bool(self.get_infection_prob()):
            neighbor.get_sick()

    def get_infection_prob(self):
        return (self.sick_level / self.model.max_shelf_sick_level) * self.model.touch_face_prob

    def step(self):
        if self.sick_level > 0:
            self.desc_counter += 1
            if self.desc_counter > self.model.virus_duration:
                self.sick_level -= 1
                self.desc_counter = 0


class BackgroundAgent(Agent):
    def __init__(self, unique_id, model, pos, type_):
        super().__init__(unique_id, model)
        self.pos = pos
        self.type = type_

