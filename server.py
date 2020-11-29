import colorsys
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from agents import CustomerAgent, ShelfAgent, BackgroundAgent, CashierAgent, HumanAgent
from shop_elem import ShopElem
import numpy as np

from model import CovidModel


class InfectElement(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "Infected agents: " + str(model.infections)


class SickElement(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "Sick agents: " + str(model.sick_customers)


class CountElement(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "Customer counter: " + str(model.customers)


sick_shelf_colors = [colorsys.hsv_to_rgb(0, s / 10, 0.65) for s in range(0, 11)]
sick_shelf_colors = ['#%02x%02x%02x' % (int(c[0] * 255), int(c[1] * 255), int(c[2] * 255)) for c in sick_shelf_colors]


def schelling_draw(agent):
    if agent is None:
        return
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}

    if isinstance(agent, HumanAgent):
        portrayal = {"Shape": "circle",
                     "text": "M" if agent.mask is True else "",
                     "text_color": "White",
                     "Color": "Red" if agent.sick is True else "Green",
                     "Filled": "true",
                     "Layer": 0
                     }
        if agent.sick:
            portrayal["Color"] = ["Red"]
        elif agent.infected:
            portrayal["Color"] = ["Yellow"]
        else:
            portrayal["Color"] = ["Green"]

        if type(agent) is CustomerAgent:
            portrayal["r"] = 1 if agent.risk_group is True else 0.6,
        elif type(agent) is CashierAgent:
            portrayal["r"] = 1
    elif type(agent) is ShelfAgent:
        portrayal["Color"] = sick_shelf_colors[agent.sick_level]
        portrayal["text"] = agent.sick_level
        portrayal["text_color"] = "White"
    elif type(agent) is BackgroundAgent:
        if agent.type == ShopElem.WALL:
            portrayal["Color"] = ["Black"]
        elif agent.type == ShopElem.ENTRY:
            portrayal["Color"] = ["Green"]
        elif agent.type == ShopElem.EXIT:
            portrayal["Color"] = ["Red"]

    return portrayal


infected_element = InfectElement()
sick_element = SickElement()
count_element = CountElement()

canvas_element = CanvasGrid(schelling_draw, 26, 37, 650, 650)
sick_chart = ChartModule(
    [
        {"Label": "infections", "Color": "Black"},
        {"Label": "deaths", "Color": "Red"},
    ]
)

model_params = {
    "num_customers": UserSettableParameter("slider", "Liczba osób w sklepie", 10, 1, 40, 1),
    "sick_percent": UserSettableParameter("slider", "Procent ludzi chorych wchodzących", 0.2, 0.00, 1.0, 0.05),
    "mask_percent": UserSettableParameter("slider", "Procent ludzi noszących maseczki", 0.5, 0.00, 1.0, 0.05),
    "risk_group_percent": UserSettableParameter("slider", "Procent należących do grupy wysokiego ryzyka", 0.2, 0.00,
                                                1.0, 0.05),
    "death_ratio": UserSettableParameter("slider", "Śmiertelność dla grupy niskiego ryzyka", 0.1, 0.00, 1.0, 0.05),
    "death_ratio_rg": UserSettableParameter("slider", "Śmiertelność dla grupy wysokiego ryzyka", 0.2, 0.00, 1.0, 0.05),
    "infect_shelf_prob": UserSettableParameter("slider", "Prawdopodobieństwo zakażenia półki", 0.2, 0.00, 1.0, 0.05),
    "virus_duration": UserSettableParameter("slider", "Czas utrzymywania się wirusa na półce", 20, 0, 100, 5),
    "sick_cashiers_num": UserSettableParameter("slider", "Liczba zarażonych kasjerów", 2, 0, 4, 1),
    "cashiers_masks": UserSettableParameter("checkbox", "Kasjerzy w maseczkach", value=True)
}

server = ModularServer(
    CovidModel, [canvas_element,infected_element,sick_element,count_element, sick_chart], "Covid", model_params
)