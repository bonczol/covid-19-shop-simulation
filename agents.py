import random

from mesa import Agent


class CustomerAgent(Agent):
    # TODO uzupenic braukjące parametry
    def __init__(self, unique_id, model, pos, sick, risk_group):
        super().__init__(unique_id, model)
        self.pos = pos
        self.sick = False
        self.risk_group = risk_group
        self.shopping_list = self.get_shopping_list()
        self.type = 10
        self.last = "up"

    # TODO uzupenic zachowania agenta
    def step(self):
        for neighbor in self.model.grid.neighbor_iter(self.pos):
            if self.sick:
                if not neighbor.sick:
                    self.model.sick += 1
                neighbor.sick = True

        if self.shopping_list:
            self.move()
        else:
            self.go_to_out()

    # TODO uzupenic tworzenie listy zakupow
    def get_shopping_list(self):
        return [self.model.shelfs[random.randint(0, len(self.model.shelfs)-1)], (0, 20)]
        # return self.model.grid.find_empty()

    def move(self):
        a = self.find_path(self.shopping_list[0])
        if len(a)>1:
            if self.model.grid.is_cell_empty(a[-2]):
                self.model.grid.move_agent(self, a[-2])
        else:
            if self.model.grid.is_cell_empty(a[0]):
                self.model.grid.move_agent(self, a[0])

    def go_to_out(self):
        pass

    def get_grid(self):
        grid =[]
        for i in self.model.grid .grid:
            a=[]
            for j in i:
                if j is None:
                    a.append(0)
                else:
                    a.append(1)
            grid.append(a)
        return grid


    def find_path(self, end):
        m = []
        a =self.get_grid()
        for i in range(len(a)):
            m.append([])
            for j in range(len(a[i])):
                m[-1].append(0)
        i, j = self.pos
        m[i][j] = 1
        k = 0
        if a[end[0]][end[1]] !=0:
            return [(i,j)]
        while m[end[0]][end[1]] == 0 :
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


# TODO
class CashierAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos


# TODO
class ShelfAgent(Agent):
    def __init__(self, unique_id, model, pos, sick):
        super().__init__(unique_id, model)
        self.pos = pos
        self.sick = sick


class BackgroundAgent(Agent):
    def __init__(self, unique_id, model, pos, type_):
        super().__init__(unique_id, model)
        self.pos = pos
        self.type = type_
