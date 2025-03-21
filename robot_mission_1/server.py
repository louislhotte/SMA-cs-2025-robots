"""
-------------------------------------------------
Group 1 - Project Name
Created on: 2025-03-11
Authors: Louis LHOTTE, Ambroise MARTIN-ROUVILLE, Edouard SEGUIER
-------------------------------------------------

Description:
This script [briefly describe the purpose of the script here].
"""

"""
server.py
Example of using Mesa's SolaraViz to visualize the RobotMission.
"""
import solara
from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from model import RobotMission 
import os

def agent_portrayal(agent):
    """Return a dict describing how each agent is drawn."""
    if agent is None:
        return {}

    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Layer": 0,
        "r": 0.5,  
        "Color": "gray",
    }

    if hasattr(agent, "zone"):
        portrayal["Color"] = "red"
    elif hasattr(agent, "waste_type"):
        portrayal["Color"] = "green"
    elif "GreenAgent" in str(type(agent)):
        portrayal["Color"] = "blue"

    return portrayal

space_component = make_space_component(
    model_cls=RobotMission,
    grid_name="grid",          
    portrayal_method=agent_portrayal,
    height=500,                
    width=500,               
)


def count_agents(model):
    """Example function returning a single numeric value for the plot."""
    return len(model.all_agents)

def count_green_agents(model):
    """Example function returning just the number of GreenAgent instances."""
    total = 0
    for agent in model.all_agents:
        if "GreenAgent" in str(type(agent)):
            total += 1
    return total

plot_component = make_plot_component("Gini")


viz = SolaraViz(
    model_cls=RobotMission,
    name="Robot Mission Visualization",
    components=[space_component, plot_component],
    model_params=[10,10,2]
)
viz

if __name__ == "__main__":
    os.system("solara run ./robot_mission_1/server.py")