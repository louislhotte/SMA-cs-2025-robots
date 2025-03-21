from mesa import Agent, Model
from mesa.space import MultiGrid
import random
from mesa.visualization import SolaraViz, make_space_component, make_plot_component
import os

class ZoneAgent(Agent):
    def __init__(self, unique_id, model, pos):
        self.unique_id = unique_id
        self.model = model
        self.pos = pos
        x, _ = pos
        self.color = "red" if x < 3 else ("green" if x < 7 else "blue")
    def step(self):
        pass

class ZonesModel(Model):
    def __init__(self, width=10, height=10):
        super().__init__()
        self.grid = MultiGrid(width, height, False)
        self.steps = 0
        c = 0
        for x in range(width):
            for y in range(height):
                a = ZoneAgent(c, self, (x, y))
                self.grid.place_agent(a, (x, y))
                c += 1
    def step(self):
        self.steps += 1

def agent_portrayal(agent):
    return {"Shape":"rect","Color":agent.color,"Filled":True,"Layer":0,"w":1,"h":1}

model = ZonesModel(10, 10)
space_component = make_space_component(agent_portrayal, model.grid, 500, 500)
plot_component = make_plot_component(lambda m: m.steps, 300, 200)
viz = SolaraViz(ZonesModel, {}, [space_component, plot_component])

viz