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
import threading
print(f"Mesa version: {mesa.__version__}")

import solara
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mesa.visualization.utils import update_counter

from model import RobotMission 
from agents import GreenRobot, YellowRobot, RedRobot
from objects import Radioactivity, WasteDisposalZone, Waste
import os 
import plotly.graph_objects as go


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

current_model = solara.reactive(model)
step_count = solara.reactive(0)
waste_history = []
journal_logs = []
action_stats = {"GreenRobot": 0, "YellowRobot": 0, "RedRobot": 0}


def log_action(message):
    journal_logs.append(f"[Step {step_count.value}] {message}")
    if len(journal_logs) > 10:
        journal_logs.pop(0)


def update_waste_history():
    counts = {"green": 0, "yellow": 0, "red": 0}
    for agent in current_model.value.schedule.agents:
        if isinstance(agent, Waste):
            counts[agent.waste_type] += 1
    waste_history.append((step_count.value, counts["green"], counts["yellow"], counts["red"]))


def step_model():
    current_model.value.step()
    step_count.value += 1
    update_waste_history()


def run_simulation(interval=0.1):
    if running.value:
        step_model()
        threading.Timer(interval, run_simulation, [interval]).start()


def render_grid():
    fig = Figure(figsize=(10, 8))
    ax = fig.add_subplot(111)

    grid_width = current_model.value.grid.width
    grid_height = current_model.value.grid.height
    zone_width = grid_width // 3
    ax.add_patch(plt.Rectangle((0, 0), zone_width, grid_height, color='lightgreen', alpha=0.3))
    ax.add_patch(plt.Rectangle((zone_width, 0), zone_width, grid_height, color='lightyellow', alpha=0.3))
    ax.add_patch(plt.Rectangle((2*zone_width, 0), zone_width, grid_height, color='lightcoral', alpha=0.3))

    for agent in current_model.value.schedule.agents:
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
                symbol = {'green': 'gs', 'yellow': 'ys', 'red': 'rs'}[agent.waste_type]
                ax.plot(agent.pos[0] + 0.5, agent.pos[1] + 0.5, symbol, markersize=8)
            elif isinstance(agent, WasteDisposalZone):
                ax.plot(agent.pos[0] + 0.5, agent.pos[1] + 0.5, 'bs', markersize=6)
        except Exception as e:
            print(f"Error drawing agent {agent.unique_id}: {e}")

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


def render_lineplot():
    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    if waste_history:
        steps, greens, yellows, reds = zip(*waste_history)
        ax.plot(steps, greens, label="Green Waste", marker='o', color='green')
        ax.plot(steps, yellows, label="Yellow Waste", marker='o', color='gold')
        ax.plot(steps, reds, label="Red Waste", marker='o', color='red')
        ax.set_title("Waste Count over Simulation Steps")
        ax.set_xlabel("Step")
        ax.set_ylabel("Waste Count")
        ax.legend()
    return fig


def render_journal():
    if not journal_logs:
        return solara.Markdown("_No activity yet._")
    return solara.Markdown("\n".join(journal_logs))


def render_agent_stats():
    fig = Figure(figsize=(5, 3))
    ax = fig.add_subplot(121)
    names = list(action_stats.keys())
    values = list(action_stats.values())
    ax.bar(names, values)
    ax.set_title("Agent Action Count")
    ax.set_ylabel("# Actions")
    return fig


running = solara.reactive(False)

@solara.component
def Page():
    width_val = solara.reactive(12)
    height_val = solara.reactive(12)
    initial_green_waste_val = solara.reactive(10)
    initial_yellow_waste_val = solara.reactive(8)
    initial_red_waste_val = solara.reactive(8)
    nb_green_agent_val = solara.reactive(2)
    nb_yellow_agent_val = solara.reactive(2)
    nb_red_agent_val = solara.reactive(2)

    def reset_model():
        global waste_history, journal_logs, action_stats
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
        journal_logs = []
        for key in action_stats:
            action_stats[key] = 0
        update_waste_history()

    def toggle_running():
        running.set(not running.value)
        if running.value:
            run_simulation()

    with solara.Column() as main:
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

        solara.Title("Robot Waste Collection Simulation")
        with solara.Row():
            solara.Button("Step", on_click=step_model)
            solara.Button("Stop" if running.value else "Play", on_click=toggle_running)
            solara.Info(f"Step: {step_count.value}")

        with solara.Row():
            with solara.Column():
                update_counter.get()
                try:
                    solara.FigureMatplotlib(render_grid())
                except Exception as e:
                    solara.Error(f"Error rendering grid: {str(e)}")
                try:
                    solara.FigureMatplotlib(render_agent_stats())
                except Exception as e:
                    solara.Error(f"Error rendering agent stats: {str(e)}")
                render_journal()
            with solara.Column():
                try:
                    solara.FigureMatplotlib(render_lineplot())
                except Exception as e:
                    solara.Error(f"Error rendering line plot: {str(e)}")

# To run the app:
# solara run run.py --port 8523