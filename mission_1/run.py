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

# Create reactive state for the model and simulation step
current_model = solara.reactive(model)
step_count = solara.reactive(0)

# Global variable to store waste count history as tuples: (step, green, yellow, red)
waste_history = []

def update_waste_history():
    """Update waste_history with the current waste counts from the model."""
    counts = {"green": 0, "yellow": 0, "red": 0}
    for agent in current_model.value.schedule.agents:
        if isinstance(agent, Waste):
            waste_type = agent.waste_type
            if waste_type in counts:
                counts[waste_type] += 1
    waste_history.append((step_count.value, counts["green"], counts["yellow"], counts["red"]))

# Function to step the model and update history
def step_model():
    current_model.value.step()
    step_count.value += 1
    update_waste_history()

# Function to render agents on the grid with legend below
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

    # Create custom legend elements
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

# Function to render the waste count line plot (evolution over steps)
def render_lineplot():
    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    if waste_history:
        # Unpack history data
        steps = [s for s, g, y, r in waste_history]
        green_counts = [g for s, g, y, r in waste_history]
        yellow_counts = [y for s, g, y, r in waste_history]
        red_counts = [r for s, g, y, r in waste_history]
        # Plot lines with markers at each step
        ax.plot(steps, green_counts, label="Green Waste", marker='o', color='green')
        ax.plot(steps, yellow_counts, label="Yellow Waste", marker='o', color='gold')
        ax.plot(steps, red_counts, label="Red Waste", marker='o', color='red')
        ax.set_title("Waste Count over Simulation Steps")
        ax.set_xlabel("Step")
        ax.set_ylabel("Waste Count")
        ax.legend()
    return fig

# Function to render a textual performance report for robot agents
def render_report():
    report_lines = []
    for agent in current_model.value.schedule.agents:
        if isinstance(agent, (GreenRobot, YellowRobot, RedRobot)):
            collected = getattr(agent.knowledge, 'collected_waste', 0)
            report_lines.append(f"{agent.__class__.__name__} {agent.unique_id}: {collected} waste collected, performing mission.")
    if not report_lines:
        report_lines.append("No agent performance data available.")
    return "\n".join(report_lines)

# The main Solara app using a sidebar for parameter controls
@solara.component
def Page():
    # Create reactive variables for model parameters
    width_val = solara.reactive(12)
    height_val = solara.reactive(10)
    initial_green_waste_val = solara.reactive(10)
    initial_yellow_waste_val = solara.reactive(8)
    initial_red_waste_val = solara.reactive(8)
    nb_green_agent_val = solara.reactive(2)
    nb_yellow_agent_val = solara.reactive(2)
    nb_red_agent_val = solara.reactive(2)

    def reset_model():
        # Reset the model using the current slider values and clear waste history
        global waste_history
        current_model.value = RobotMission(
            width=width_val.value,
            height=height_val.value,
            initial_green_waste=initial_green_waste_val.value,
            initial_yellow_waste=initial_yellow_waste_val.value,
            initial_red_waste=initial_red_waste_val.value,
            nb_green_agent=nb_green_agent_val.value,
            nb_yellow_agent=nb_yellow_agent_val.value,
            nb_red_agent=nb_red_agent_val.value
        )
        step_count.value = 0
        waste_history = []
        update_waste_history()  # capture initial counts

    with solara.Column() as main:
        # Sidebar with parameter controls
        with solara.Sidebar():
            solara.Markdown("## Parameters")
            solara.SliderInt("Width", value=width_val, min=5, max=30)
            solara.SliderInt("Height", value=height_val, min=5, max=30)
            solara.SliderInt("Initial Green Waste", value=initial_green_waste_val, min=0, max=50)
            solara.SliderInt("Initial Yellow Waste", value=initial_yellow_waste_val, min=0, max=50)
            solara.SliderInt("Initial Red Waste", value=initial_red_waste_val, min=0, max=50)
            solara.SliderInt("Number of Green Agents", value=nb_green_agent_val, min=1, max=3)
            solara.SliderInt("Number of Yellow Agents", value=nb_yellow_agent_val, min=1, max=3)
            solara.SliderInt("Number of Red Agents", value=nb_red_agent_val, min=1, max=3)
            solara.Button("Reset", on_click=reset_model)

        # Main content area
        solara.Title("Robot Waste Collection Simulation")
        with solara.Row():
            solara.Button("Step", on_click=step_model)
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
                    line_fig = render_lineplot()
                    solara.FigureMatplotlib(line_fig)
                except Exception as e:
                    solara.Error(f"Error rendering line plot: {str(e)}")
        try:
            report_text = render_report()
            solara.Markdown(report_text)
        except Exception as e:
            solara.Error(f"Error rendering report: {str(e)}")
    return main

# To run the app:
# solara run run.py --port 8523
