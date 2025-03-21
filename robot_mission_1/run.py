"""
-------------------------------------------------
Group 1 - Project Name
Created on: 2025-03-11
Authors: Louis LHOTTE, Ambroise MARTIN-ROUVILLE, Edouard SEGUIER
-------------------------------------------------

Description:
This script [briefly describe the purpose of the script here].
"""
from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from model import RobotMission
from agents import GreenAgent, YellowAgent, RedAgent, Waste
from objects import RadioactivityAgent, WasteDisposalZone
import mesa
import os

def agent_portrayal(agent):
    """
    This function replaces what you were previously passing to CanvasGrid.
    For each agent, return a dictionary describing how it should be drawn.
    """
    if isinstance(agent, GreenAgent):
        return {"Shape": "circle", "Color": "green", "Filled": "true", "Layer": 2, "r": 0.5}
    elif isinstance(agent, YellowAgent):
        return {"Shape": "circle", "Color": "yellow", "Filled": "true", "Layer": 2, "r": 0.5}
    elif isinstance(agent, RedAgent):
        return {"Shape": "circle", "Color": "red", "Filled": "true", "Layer": 2, "r": 0.5}
    elif isinstance(agent, Waste):
        # color is agent.waste_type, if you store e.g. "green"/"yellow"/"red" or similar
        return {"Shape": "rect", "Color": agent.waste_type, "Filled": "true", "Layer": 1, "w": 0.3, "h": 0.3}
    elif isinstance(agent, WasteDisposalZone):
        return {"Shape": "rect", "Color": "blue", "Filled": "true", "Layer": 1, "w": 1, "h": 1}
    elif isinstance(agent, RadioactivityAgent):
        # Assign color based on the zone
        if agent.zone == "z1":
            color = "lightgreen"
        elif agent.zone == "z2":
            color = "lightyellow"
        elif agent.zone == "z3":
            color = "lightcoral"
        else:
            color = "white"
        return {"Shape": "rect", "Color": color, "Filled": "true", "Layer": 0, "w": 1, "h": 1}
    else:
        # Default
        return {"Shape": "rect", "Color": "white", "Filled": "false", "Layer": 0, "w": 1, "h": 1}


def get_waste_count(model):
    """Example helper function for your chart: returns how many Waste agents remain."""
    return sum(isinstance(agent, Waste) for agent in model.schedule.agents)


# 1) Replaces the old CanvasGrid:
#    We specify how to portray agents, the size of the grid, and how many pixels to draw, etc.
space_component = make_space_component(
    portrayal_method=agent_portrayal,  # Your portrayal function
    grid_width=12,                     # Model grid width
    grid_height=10,                    # Model grid height
    canvas_width=500,                  # Pixel width of the drawn space
    canvas_height=500                  # Pixel height of the drawn space
)

plot_component = make_plot_component(
    measure={"Waste": get_waste_count}
)

# 3) Model parameters (replaces the old Sliders).
#    If you want them user-adjustable, you can see Mesa’s newer parameter APIs.
model_params = {
    "width": 12,
    "height": 10,
    "initial_green_waste": 10,
    "initial_yellow_waste": 8,
    "initial_red_waste": 8,
    "nb_green_agent": 2,
    "nb_yellow_agent": 2,
    "nb_red_agent": 2
}

app = SolaraViz(
    RobotMission,         
    visualization_elements=[        
        space_component,
        plot_component
    ],
    name="Robot Waste Collection Mission",
    parameters=model_params         
)

if __name__ == "__main__":
    os.system("solara run run.py")