import random
from mesa.space import SingleGrid
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from agents import CustomerAgent, CashierAgent, ShelfAgent, BackgroundAgent, TestAgent
from shop_generator import ShopGenerator
from shop_elem import ShopElem
from shop_parser import ShopParser
from helper import  random_bool, shuffled_bools


class CovidModel(Model):
    def __init__(self,
                 width,
                 height,
                 sick_percent=0.5,
                 mask_percent=0.5,
                 risk_group_percent=0.5,
                 sick_shelf_percent=0.1,
                 death_ratio=0.3,
                 num_customers=10):

        self.num_customers = num_customers
        self.mask_percent = mask_percent
        self.risk_group_percent = risk_group_percent
        self.sick_percent = sick_percent
        self.sick_shelf_percent = sick_shelf_percent
        self.death_ratio = death_ratio

        # Infection params - by cough
        self.carrier_mask_neighbour_mask = 0.015
        self.carrier_mask_neighbour_no_mask = 0.05
        self.carrier_no_mask_neighbour_mask = 0.7
        self.carrier_no_mask_neighbour_no_mask = 0.85

        # Infection params - by touch
        self.infect_shelf_prob = 0.5
        self.max_shelf_sick_level = 10
        self.touch_face_prob = 0.5

        # Customer's shopping list distribution params
        self.max_shopping_list = 13
        self.mean_shopping_list = 7
        self.std_dev_shopping_list = 2.5

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
        self.infections = 0
        self.deaths = 0
        self.datacollector = DataCollector(
            {"infections": "infections"},
            # {"deaths": "deaths"},
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
        spawn_coords = random.choices(self.shop.elements[ShopElem.SHOPPING_AREA], k=self.num_customers)
        sick_arr = shuffled_bools(self.num_customers, self.sick_percent)
        mask_arr = shuffled_bools(self.num_customers, self.mask_percent)
        risk_group_arr = shuffled_bools(self.num_customers, self.risk_group_percent)

        for coord, sick, mask, risk_group in zip(spawn_coords, sick_arr, mask_arr, risk_group_arr):
            customer = CustomerAgent(self.get_id(), self, coord, sick, mask, risk_group)
            self.grid.place_agent(customer, coord)
            self.schedule.add(customer)

    def spawn_cashiers(self):
        for coord in self.shop.elements[ShopElem.CASHIER]:
            cashier = CashierAgent(self.get_id(), self, coord)
            self.grid.place_agent(cashier, coord)
            self.schedule.add(cashier)

    def spawn_shelves(self):
        sick_arr = shuffled_bools(len(self.shop.elements[ShopElem.SHELF]), self.sick_shelf_percent)
        for shelf, sick in zip(self.shop.elements[ShopElem.SHELF], sick_arr):
            coord, _ = shelf
            sick_level = random.randint(1, self.max_shelf_sick_level) if sick else 0
            shelf_agent = ShelfAgent(self.get_id(), self, coord, sick_level=sick_level)
            self.grid.place_agent(shelf_agent, coord)
            self.schedule.add(shelf_agent)

    def step(self):
        # TODO
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
