from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from model import CovidModel


class SickElement(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "Sick agents: " + str(model.sick)


def schelling_draw(agent):
    """
    Portrayal Method for canvas
    """
    if agent is None:
        return
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}

    if agent.type == 1:
        portrayal["Color"] = ["Grey"]
    elif agent.type == 2:
        portrayal["Color"] = ["Black"]
    elif agent.type == 3:
        portrayal["Color"] = ["Yellow"]
    elif agent.type == 4:
        portrayal["Color"] = ["Green"]
    elif agent.type == 5:
        portrayal["Color"] = ["Red"]
    elif agent.type == 6:
        portrayal["Color"] = ["Purple"]
    elif agent.type == 7:
        portrayal["Color"] = ["Purple"]
    else:
        portrayal = {"Shape": "circle", "r": 1, "Filled": "true", "Layer": 0, "Color" : "Blue"}

    return portrayal


sick_element = SickElement()
canvas_element = CanvasGrid(schelling_draw, 24, 35, 500, 500)
sick_chart = ChartModule([{"Label": "sick", "Color": "Black"}])

# TODO uzupenic braukjące parametry
model_params = {
    "height": 24,
    "width": 35
    # ,
    # "density": UserSettableParameter("slider", "Agent density", 0.8, 0.1, 1.0, 0.1),
    # "minority_pc": UserSettableParameter(
    #     "slider", "Fraction minority", 0.2, 0.00, 1.0, 0.05
    # ),
    # "homophily": UserSettableParameter("slider", "Homophily", 3, 0, 8, 1),
}

server = ModularServer(
    CovidModel, [canvas_element, sick_element, sick_chart], "Covid", model_params
)
