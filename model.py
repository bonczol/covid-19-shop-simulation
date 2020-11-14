from mesa.space import SingleGrid
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector


class CovidModel(Model):
    def __init__(self, N=10, width=10, height=10):
        self.num_agents = N
        self.grid = SingleGrid(height, width, True)
        self.schedule = RandomActivation(self)

        # Create agents
        for i in range(self.num_agents):
            print(i)

        self.running = True

    def step(self):
        self.schedule.step()
