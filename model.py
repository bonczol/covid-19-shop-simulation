import random
from mesa.space import SingleGrid
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from agents import CustomerAgent, CashierAgent, ShelfAgent, BackgroundAgent, TestAgent
from shop_generator import ShopGenerator
from shop_elem import ShopElem
from shop_parser import ShopParser


class CovidModel(Model):
    def __init__(self, height, width, n=10):
        self.num_agents = n
        shop_map = ShopGenerator(rows=2,
                                 shelves_in_row=5,
                                 shelf_length=10,
                                 space_between_rows=3,
                                 space_between_shelves=2
                                 ).map_
        self.shop = ShopParser()
        self.shop.parse(shop_map)

        self.width, self.height = self.shop.map.shape
        self.grid = SingleGrid(self.width, self.height, False)
        self.schedule = RandomActivation(self)

        # TODO dodac zbieranie statystyk
        self.sick = 0
        self.datacollector = DataCollector(
            {"sick": "sick"},
            {"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]},
        )

        self.agent_id = 0
        self.spawn_agents()

        self.running = True
        self.datacollector.collect(self)

    def get_id(self):
        id_ = self.agent_id
        self.agent_id += 1
        return id_

    def spawn_agents(self):
        self.spawn_background(ShopElem.WALL)
        self.spawn_background(ShopElem.ENTRY)
        self.spawn_background(ShopElem.EXIT)
        self.spawn_shelves()
        self.spawn_cashiers()
        self.spawn_customers()

    def spawn_background(self, type_):
        for coord in self.shop.elements[type_]:
            agent = BackgroundAgent(self.get_id(), self, coord, type_=type_)
            self.grid.place_agent(agent, coord)

    def spawn_customers(self):
        spawn_coords = random.choices(self.shop.elements[ShopElem.SHOPPING_AREA], k=self.num_agents)
        for coord in spawn_coords:
            customer = CustomerAgent(self.get_id(), self, coord, True, True)
            self.grid.place_agent(customer, coord)
            self.schedule.add(customer)

    def spawn_cashiers(self):
        for coord in self.shop.elements[ShopElem.CASHIER]:
            cashier = CashierAgent(self.get_id(), self, coord)
            self.grid.place_agent(cashier, coord)
            self.schedule.add(cashier)

    def spawn_shelves(self):
        for coord, _ in self.shop.elements[ShopElem.SHELF]:
            shelf = ShelfAgent(self.get_id(), self, coord, sick=False)
            self.grid.place_agent(shelf, coord)
            self.schedule.add(shelf)


    def step(self):
        # TODO
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
