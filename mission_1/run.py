"""
-------------------------------------------------
Group 1 - Project Name
Created on: 2025-03-11
Authors: Louis LHOTTE, Ambroise MARTIN-ROUVILLE, Edouard SEGUIER
-------------------------------------------------

Description:
This script contains the frontend of the solara application
"""

from matplotlib.lines import Line2D
import mesa
print(f"Mesa version: {mesa.__version__}")

import solara
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mesa.visualization.utils import update_counter

from model import RobotMission 
from agents import GreenRobot, YellowRobot, RedRobot
from objects import Radioactivity, WasteDisposalZone, Waste
import os 

# Create a model instance with default parameters
model = RobotMission(
    width=12,
    height=10,
    initial_green_waste=10,
    initial_yellow_waste=8,
    initial_red_waste=8,
    nb_green_agent=2,
    nb_yellow_agent=2,
    nb_red_agent=2
)

# Create some reactive state for the model
current_model = solara.reactive(model)
step_count = solara.reactive(0)

# Function to step the model
def step_model():
    current_model.value.step()
    step_count.value += 1

# Function to render agents on the grid
def render_grid():
    fig = Figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    
    # Plot the grid
    grid_width = current_model.value.grid.width
    grid_height = current_model.value.grid.height
    
    # Draw zones
    zone_width = grid_width // 3
    ax.add_patch(plt.Rectangle((0, 0), zone_width, grid_height, color='lightgreen', alpha=0.3))
    ax.add_patch(plt.Rectangle((zone_width, 0), zone_width, grid_height, color='lightyellow', alpha=0.3))
    ax.add_patch(plt.Rectangle((2*zone_width, 0), zone_width, grid_height, color='lightcoral', alpha=0.3))
    
    # Draw agents
    for agent in current_model.value.schedule.agents:
        # Skip agents with no position
        if not hasattr(agent, 'pos') or agent.pos is None:
            continue
            
        try:
            if isinstance(agent, GreenRobot):
                ax.plot(agent.pos[0] + 0.5, agent.pos[1] + 0.5, 'go', markersize=10)
            elif isinstance(agent, YellowRobot):
                ax.plot(agent.pos[0] + 0.5, agent.pos[1] + 0.5, 'yo', markersize=10)
            elif isinstance(agent, RedRobot):
                ax.plot(agent.pos[0] + 0.5, agent.pos[1] + 0.5, 'ro', markersize=10)
            elif isinstance(agent, Waste):
                if agent.waste_type == "green":
                    ax.plot(agent.pos[0] + 0.5, agent.pos[1] + 0.5, 'gs', markersize=8)
                elif agent.waste_type == "yellow":
                    ax.plot(agent.pos[0] + 0.5, agent.pos[1] + 0.5, 'ys', markersize=8)
                elif agent.waste_type == "red":
                    ax.plot(agent.pos[0] + 0.5, agent.pos[1] + 0.5, 'rs', markersize=8)
            elif isinstance(agent, WasteDisposalZone):
                ax.plot(agent.pos[0] + 0.5, agent.pos[1] + 0.5, 'bs', markersize=6)
        except Exception as e:
            print(f"Error drawing agent {agent.unique_id}: {e}")
    
    # Set grid properties
    ax.set_xlim(0, grid_width)
    ax.set_ylim(0, grid_height)
    ax.set_xticks(range(grid_width + 1))
    ax.set_yticks(range(grid_height + 1))
    ax.grid(True)
    ax.set_title(f'Robot Waste Simulation - Step {step_count.value}')

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Green Robot', markerfacecolor='green', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Yellow Robot', markerfacecolor='yellow', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Red Robot', markerfacecolor='red', markersize=10),
        Line2D([0], [0], marker='s', color='w', label='Green Waste', markerfacecolor='green', markersize=8),
        Line2D([0], [0], marker='s', color='w', label='Yellow Waste', markerfacecolor='yellow', markersize=8),
        Line2D([0], [0], marker='s', color='w', label='Red Waste', markerfacecolor='red', markersize=8),
        Line2D([0], [0], marker='s', color='w', label='Waste Disposal Zone', markerfacecolor='blue', markersize=6),
    ]
    
    ax.legend(handles=legend_elements, loc='center', bbox_to_anchor=(0.5, -0.1), ncol=4)
    
    return fig

# Function to render the waste count barplot
def render_barplot():
    # Count waste by type
    waste_counts = {"green": 0, "yellow": 0, "red": 0}
    for agent in current_model.value.schedule.agents:
        if isinstance(agent, Waste):
            waste_type = agent.waste_type
            if waste_type in waste_counts:
                waste_counts[waste_type] += 1
    
    # Create barplot
    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    types = list(waste_counts.keys())
    counts = [waste_counts[t] for t in types]
    ax.bar(types, counts, color=['green', 'gold', 'red'])
    ax.set_title("Waste Count")
    ax.set_xlabel("Waste Type")
    ax.set_ylabel("Count")
    
    return fig

# The main Solara app
@solara.component
def Page():
    # Create UI controls
    with solara.Column():
        solara.Title("Robot Waste Collection Simulation")
        
        # Controls in a row
        with solara.Row():
            # Step button
            solara.Button("Step", on_click=step_model)
            
            # Reset button (recreates the model)
            def reset_model():
                current_model.value = RobotMission(
                    width=12,
                    height=10,
                    initial_green_waste=10,
                    initial_yellow_waste=8,
                    initial_red_waste=8,
                    nb_green_agent=2,
                    nb_yellow_agent=2,
                    nb_red_agent=2
                )
                step_count.value = 0
                
            solara.Button("Reset", on_click=reset_model)
            
            # Display step count
            solara.Info(f"Step: {step_count.value}")
        
        with solara.Row():
            with solara.Column():
                update_counter.get() 
                try:
                    grid_fig = render_grid()
                    solara.FigureMatplotlib(grid_fig)
                except Exception as e:
                    solara.Error(f"Error rendering grid: {str(e)}")
            with solara.Column():
                try:
                    barplot_fig = render_barplot()
                    solara.FigureMatplotlib(barplot_fig)
                except Exception as e:
                    solara.Error(f"Error rendering barplot: {str(e)}")

# The key fix: use solara.run() instead of os.system
# if __name__ == "__main__":
#     os.system('solara run run.py --port 8523')
