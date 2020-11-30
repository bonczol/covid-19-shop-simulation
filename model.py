import random
from mesa.space import SingleGrid
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from agents import CustomerAgent, CashierAgent, ShelfAgent, BackgroundAgent
from shop_generator import ShopGenerator
from shop_elem import ShopElem
from shop_parser import ShopParser
from helper import random_bool, shuffled_bools


class CovidModel(Model):
    def __init__(self,
                 sick_percent=0.15,
                 mask_percent=0.5,
                 risk_group_percent=0.5,
                 sick_shelf_percent=0,
                 sick_cashiers_num=2,
                 death_ratio=0.1,
                 death_ratio_rg=0.3,
                 infect_shelf_prob=0.3,
                 touch_face_prob=0.3,
                 max_shelf_sick_level=10,
                 virus_duration=50,
                 cashiers_masks=False,
                 num_cashiers=4,
                 num_customers=20):

        self.num_customers = num_customers
        self.num_cashiers = num_cashiers
        self.mask_percent = mask_percent
        self.risk_group_percent = risk_group_percent
        self.sick_percent = sick_percent
        self.sick_shelf_percent = sick_shelf_percent
        self.sick_cashiers_num = sick_cashiers_num
        self.death_ratio = death_ratio
        self.death_ratio_rg = death_ratio_rg
        self.infect_shelf_prob = infect_shelf_prob
        self.touch_face_prob = touch_face_prob
        self.max_shelf_sick_level = max_shelf_sick_level
        self.virus_duration = virus_duration
        self.cashiers_mask = cashiers_masks
        self.c = 0

        # Infection params - by cough
        self.carrier_mask_neighbour_mask = 0.015
        self.carrier_mask_neighbour_no_mask = 0.05
        self.carrier_no_mask_neighbour_mask = 0.3
        self.carrier_no_mask_neighbour_no_mask = 0.9

        # Customer's shopping list distribution params
        self.max_shopping_list = 13
        self.mean_shopping_list = 7
        self.std_dev_shopping_list = 2.5

        shop_map = ShopGenerator(rows=2,
                                 shelves_in_row=5,
                                 shelf_length=10,
                                 space_between_rows=3,
                                 space_between_shelves=2,
                                 checkouts_num=num_cashiers
                                 ).map_
        self.shop = ShopParser()
        self.shop.parse(shop_map)

        self.width, self.height = self.shop.map.shape
        self.grid = SingleGrid(self.width, self.height, False)
        self.schedule = RandomActivation(self)

        self.infections = 0
        self.deaths = 0
        self.customers = num_customers
        self.sick_customers = 0
        self.datacollector = DataCollector(
            model_reporters={
                "infections": "infections",
                "deaths": "deaths",
                "customers": "customers",
                "sick_customers": "sick_customers"
            }
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
        spawn_coords = random.sample(self.shop.elements[ShopElem.SHOPPING_AREA], self.num_customers)
        sick_arr = shuffled_bools(self.num_customers, self.sick_percent)
        mask_arr = shuffled_bools(self.num_customers, self.mask_percent)
        risk_group_arr = shuffled_bools(self.num_customers, self.risk_group_percent)

        for coord, sick, mask, risk_group in zip(spawn_coords, sick_arr, mask_arr, risk_group_arr):
            customer = CustomerAgent(self.get_id(), self, coord, sick, mask, risk_group)
            self.grid.place_agent(customer, coord)
            self.schedule.add(customer)
            if sick: self.sick_customers += 1

    def spawn_cashiers(self):
        sick_arr = shuffled_bools(self.num_cashiers, self.sick_cashiers_num / self.num_cashiers)
        for coord, sick in zip(self.shop.elements[ShopElem.CASHIER], sick_arr):
            cashier = CashierAgent(self.get_id(), self, coord, sick, self.cashiers_mask)
            self.grid.place_agent(cashier, coord)
            self.schedule.add(cashier)

    def spawn_shelves(self):
        num_shelves = len(self.shop.elements[ShopElem.SHELF])
        sick_arr = shuffled_bools(num_shelves, self.sick_shelf_percent)

        for shelf, sick in zip(self.shop.elements[ShopElem.SHELF], sick_arr):
            coord, _ = shelf
            sick_level = random.randint(1, self.max_shelf_sick_level) if sick else 0
            desc_counter = random.randint(1, self.virus_duration) if sick else 0
            shelf_agent = ShelfAgent(self.get_id(), self, coord, sick_level=sick_level, desc_counter=desc_counter)
            self.grid.place_agent(shelf_agent, coord)
            self.schedule.add(shelf_agent)

    def add_new_customer(self):
        x, y = self.shop.elements[ShopElem.ENTRY][0]
        if self.grid.is_cell_empty((x, y - 1)):
            sick = random_bool(self.sick_percent)
            mask = random_bool(self.mask_percent)
            risk_group = random_bool(self.risk_group_percent)
            customer = CustomerAgent(self.get_id(), self, (x, y - 1), sick, mask, risk_group)
            self.grid.place_agent(customer, (x, y - 1))
            self.schedule.add(customer)
            self.customers += 1
            if sick: self.sick_customers += 1
            return True
        else:
            return False

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        for neighbor in self.grid.neighbor_iter(self.shop.elements[ShopElem.EXIT][0]):
            if type(neighbor) == CustomerAgent:
                self.grid.remove_agent(neighbor)
                self.schedule.remove(neighbor)
                self.c = +1

        if self.c > 0:
            if self.add_new_customer():
                self.c -= 1

        if self.customers > 200:
            self.running = False