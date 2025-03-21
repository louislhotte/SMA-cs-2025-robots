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

# Function to render agents
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
        
        # Grid visualization
        update_counter.get()  # Force update when the model changes
        try:
            grid_fig = render_grid()
            solara.FigureMatplotlib(grid_fig)
        except Exception as e:
            solara.Error(f"Error rendering grid: {str(e)}")

# The key fix: use solara.run() instead of os.system
# if __name__ == "__main__":
#     os.system('solara run run.py --port 8523')