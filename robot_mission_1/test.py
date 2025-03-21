import mesa
print(f"Mesa version: {mesa.__version__}")

from mesa.visualization import SolaraViz, make_plot_component, make_space_component
def compute_gini(model):
    agent_waste = [agent.waste for agent in model.agents if hasattr(agent, 'waste')]
    if not agent_waste:
        return 0
    x = sorted(agent_waste)
    N = len(agent_waste)
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B

class RobotAgent(mesa.Agent):
    def __init__(self, model, color):
        super().__init__(model)
        self.color = color
        self.waste = 1
    
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()

class Waste(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.color = "black"

class WasteModel(mesa.Model):
    def __init__(self, num_green=1, num_yellow=1, num_red=1, width=10, height=10, seed=None):
        super().__init__(seed=seed)
        self.grid = mesa.space.MultiGrid(width, height, True)
        
        thirds = width // 3
        
        agent_configs = {
            "green": (0, thirds, num_green),  # Left third
            "yellow": (thirds, 2 * thirds, num_yellow),  # Middle third
            "red": (2 * thirds, width, num_red),  # Right third
        }
        
        for color, (x_min, x_max, count) in agent_configs.items():
            x_positions = self.rng.integers(x_min, x_max, size=count)
            y_positions = self.rng.integers(0, height, size=count)
            for x, y in zip(x_positions, y_positions):
                self.grid.place_agent(RobotAgent(self, color), (x, y))
        
        waste_count = self.rng.integers(5, 15)
        waste_x = self.rng.integers(0, width, size=waste_count)
        waste_y = self.rng.integers(0, height, size=waste_count)
        for x, y in zip(waste_x, waste_y):
            self.grid.place_agent(Waste(self), (x, y))
        
        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": compute_gini}, agent_reporters={}
        )
        self.datacollector.collect(self)
    
    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)

def agent_portrayal(agent):
    portrayal = {}

    if isinstance(agent, RobotAgent):
        portrayal["size"] = 50
        portrayal["color"] = agent.color
    elif isinstance(agent, Waste):
        portrayal["size"] = 10
        portrayal["color"] = "black"
    else:
        x, _ = agent  # Extract position
        width_third = waste_model.grid.width // 3
        if x < width_third:
            portrayal["color"] = "lightgreen"  # Left third
        elif x < 2 * width_third:
            portrayal["color"] = "yellow"  # Middle third
        else:
            portrayal["color"] = "red"  # Right third
        portrayal["size"] = 1  # Ensure it appears as a background layer
    
    return portrayal


model_params = {
    "num_green": {
        "type": "SliderInt",
        "value": 2,
        "label": "Number of Green Agents:",
        "min": 1,
        "max": 10,
        "step": 1,
    },
    "num_yellow": {
        "type": "SliderInt",
        "value": 2,
        "label": "Number of Yellow Agents:",
        "min": 1,
        "max": 10,
        "step": 1,
    },
    "num_red": {
        "type": "SliderInt",
        "value": 2,
        "label": "Number of Red Agents:",
        "min": 1,
        "max": 10,
        "step": 1,
    },
    "width": 10,
    "height": 10,
}

waste_model = WasteModel(num_green=2, num_yellow=2, num_red=2, width=10, height=10)
SpaceGraph = make_space_component(agent_portrayal)
GiniPlot = make_plot_component("Gini")

page = SolaraViz(
    waste_model,
    components=[SpaceGraph],
    model_params=model_params,
    name="Waste Collector Terrain",
)
page