from mesa.space import SingleGrid
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from agent import CustomerAgent, BackgroundAgent
from shop_generator import ShopMap


class CovidModel(Model):
    def __init__(self, N=10, width=40, height=50):
        self.num_agents = N
        self.grid = SingleGrid(height, width, True)
        self.schedule = RandomActivation(self)
        self.height = height
        self.width = width
        self.shelfs = []
        self.shop_map = ShopMap(rows=2,
                                shelves_in_row=5,
                                shelf_length=10,
                                space_between_rows=3,
                                space_between_shelves=2)

        # TODO dodac zbieranie statystyk
        self.sick = 0
        self.datacollector = DataCollector(
            {"sick": "sick"},  # Model-level count of happy agents
            # For testing purposes, agent's individual x and y
            {"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]},
        )

        # TODO ulepszyc ustawinie poczatkowej mapki
        h, w = self.shop_map.shop_map.shape
        for i in range(h):
            for j in range(w):
                type = self.shop_map.shop_map[i, j]
                a = h - 1 - i
                if type != 0:
                    agent = BackgroundAgent(i, self, (j, a), type)
                    self.grid.position_agent(agent, j, a)

                if type == 1:
                    if j-1 > -1 and self.shop_map.shop_map[i, j-1] == 0:
                        self.shelfs.append((j-1, a))
                    elif j+1<w and self.shop_map.shop_map[i, j+1] == 0:
                        self.shelfs.append((j+1, a))
                    elif self.shop_map.shop_map[i +1, j] == 0:
                        self.shelfs.append((j, a - 1))

        # TODO poprawic wstawianie agentow na poczatek
        for i in range(N):
            pos = self.grid.find_empty()
            agent = CustomerAgent(i, self, pos, True, True)
            self.grid.position_agent(agent, pos)
            self.schedule.add(agent)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        # TODO
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
