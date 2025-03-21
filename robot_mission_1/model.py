"""
-------------------------------------------------
Group 1 - Project Name
Created on: 2025-03-11
Authors: Louis LHOTTE, Ambroise MARTIN-ROUVILLE, Edouard SEGUIER
-------------------------------------------------

Description:
This script [briefly describe the purpose of the script here].
"""

# Your Python code starts below
"""
model.py
Defines the RobotMission model and its logic.
"""
from mesa import Agent, Model
from mesa.space import MultiGrid
import random
from agents import GreenAgent, YellowAgent, RedAgent, RandomActivationScheduler
from objects import Waste, WasteDisposalZone, RadioactivityAgent 
from mesa.datacollection import DataCollector

class RobotMission(Model):
    def __init__(
        self, 
        width,
        height,
        initial_green_waste,
        initial_yellow_waste,
        initial_red_waste,
        nb_yellow_agent,
        nb_green_agent,
        nb_red_agent
    ):
        super().__init__() 
        self.grid = MultiGrid(width, height, torus=False)
        
        # Pheromone levels
        self.pheromone_levels = {
            'green': {(x, y): 0 for x in range(width) for y in range(height)},
            'yellow': {(x, y): 0 for x in range(width) for y in range(height)},
            'red': {(x, y): 0 for x in range(width) for y in range(height)}
        }
        self.pheromone_decay_rate = 0.1  # 10% decay rate per step
        self.schedule = RandomActivationScheduler(self)

        self.initial_green_waste = initial_green_waste
        self.initial_yellow_waste = initial_yellow_waste
        self.initial_red_waste = initial_red_waste
        self.nb_yellow_agent = nb_yellow_agent
        self.nb_green_agent = nb_green_agent
        self.nb_red_agent = nb_red_agent

        l = self.grid.width // 3
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                # Zone assignment based on x coordinate
                if x < l:
                    zone = "z1"
                elif l <= x < 2 * l:
                    zone = "z2"
                else:  # x >= 2*l
                    zone = "z3"

                radioactivity_agent = RadioactivityAgent(self.schedule.get_agent_count(), self, zone)
                self.grid.place_agent(radioactivity_agent, (x, y))
                self.schedule.add(radioactivity_agent)

        self.datacollector = DataCollector(
            {
                "Waste": lambda m: m.schedule.get_type_count(Waste),
            }
        )

        # Helper function for finding empty cells in a given (x-range, y-range)
        def find_empty_cell(x_start, x_end, height, grid):
            while True:
                x = random.randrange(x_start, x_end + 1)
                y = random.randrange(0, height)
                cell_contents = grid.get_cell_list_contents((x, y))
                # Check if a Robot is in that cell
                if not any(isinstance(agent, (GreenAgent, YellowAgent, RedAgent)) for agent in cell_contents):
                    return x, y

        # Place Green Robots in z1
        z_width = l
        for _ in range(self.nb_green_agent):
            x, y = find_empty_cell(0, z_width - 1, self.grid.height, self.grid)
            robot = GreenAgent(self.schedule.get_agent_count(), self)
            self.schedule.add(robot)
            self.grid.place_agent(robot, (x, y))

        # Place Yellow Robots (z1 or z2)
        for _ in range(self.nb_yellow_agent):
            x, y = find_empty_cell(0, 2 * z_width - 1, self.grid.height, self.grid)
            robot = YellowAgent(self.schedule.get_agent_count(), self)
            self.schedule.add(robot)
            self.grid.place_agent(robot, (x, y))

        # Place Red Robots anywhere in the grid
        for _ in range(self.nb_red_agent):
            x, y = find_empty_cell(0, self.grid.width - 1, self.grid.height, self.grid)
            robot = RedAgent(self.schedule.get_agent_count(), self)
            self.schedule.add(robot)
            self.grid.place_agent(robot, (x, y))

        # Randomly placing initial wastes
        for _ in range(initial_green_waste):
            self.place_waste_in_zone("green", 0, z_width - 1, self.grid.height)
        for _ in range(initial_yellow_waste):
            self.place_waste_in_zone("yellow", z_width, 2 * z_width - 1, self.grid.height)
        for _ in range(initial_red_waste):
            self.place_waste_in_zone("red", 2 * z_width, width - 1, self.grid.height)

        # Define disposal zones
        for y in range(self.grid.height):
            # Disposal zone for z1
            dz1_pos = (z_width - 1, y)
            dz1_agent = WasteDisposalZone(self.schedule.get_agent_count(), self)
            self.grid.place_agent(dz1_agent, dz1_pos)
            self.schedule.add(dz1_agent)

            # Disposal zone for z2
            dz2_pos = (2 * z_width - 1, y)
            dz2_agent = WasteDisposalZone(self.schedule.get_agent_count(), self)
            self.grid.place_agent(dz2_agent, dz2_pos)
            self.schedule.add(dz2_agent)

            # Disposal zone for z3
            dz3_pos = (self.grid.width - 1, y)
            dz3_agent = WasteDisposalZone(self.schedule.get_agent_count(), self)
            self.grid.place_agent(dz3_agent, dz3_pos)
            self.schedule.add(dz3_agent)

    def print_zones(self):
        print("Current zone types by cell:")
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_contents = self.grid.get_cell_list_contents((x, y))
                # Find the Radioactivity agent
                radioactivity_agent = next((agent for agent in cell_contents if isinstance(agent, RadioactivityAgent)), None)
                if radioactivity_agent is not None:
                    print(f"Cell ({x}, {y}) is in zone {radioactivity_agent.zone}")

    def decay_pheromones(self):
        for (x, y), level in self.pheromone_levels['green'].items():
            self.pheromone_levels['green'][(x, y)] = max(level - self.pheromone_decay_rate, 0)
        for (x, y), level in self.pheromone_levels['yellow'].items():
            self.pheromone_levels['yellow'][(x, y)] = max(level - self.pheromone_decay_rate, 0)
        for (x, y), level in self.pheromone_levels['red'].items():
            self.pheromone_levels['red'][(x, y)] = max(level - self.pheromone_decay_rate, 0)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        self.decay_pheromones()

    def place_waste_in_zone(self, waste_type, x_start, x_end, height):
        waste = Waste(self.schedule.get_agent_count(), self, waste_type=waste_type)
        while True:
            pos = (random.randrange(x_start, x_end + 1), random.randrange(height))
            self.grid.place_agent(waste, pos)
            self.schedule.add(waste)
            break

    def perform_action(self, agent, action):
        """Model processes the action requested by the agent."""
        if action == "collect_waste":
            contents = self.grid.get_cell_list_contents(agent.pos)
            target_waste_type = (
                "green"
                if isinstance(agent, GreenAgent)
                else ("yellow" if isinstance(agent, YellowAgent) else "red")
            )
            for content in contents:
                if (
                    isinstance(content, Waste)
                    and content.waste_type == target_waste_type
                    and len(agent.knowledge["collected_waste"]) < 2
                ):
                    agent.knowledge["collected_waste"].append(content)
                    self.grid.remove_agent(content)
                    self.schedule.remove(content)
                    print(agent, agent.knowledge["collected_waste"])
                    break  
        
        elif action == "transform_waste":
            if isinstance(agent, GreenAgent) and len(agent.knowledge["collected_waste"]) == 2:
                agent.knowledge["collected_waste"].clear()
                yellow_waste = Waste(self.schedule.get_agent_count(), self, waste_type="yellow")
                self.schedule.add(yellow_waste)
                agent.knowledge["collected_waste"].append(yellow_waste)
                print(agent, agent.knowledge["collected_waste"])
            if isinstance(agent, YellowAgent) and len(agent.knowledge["collected_waste"]) == 2:
                agent.knowledge["collected_waste"].clear()
                red_waste = Waste(self.schedule.get_agent_count(), self, waste_type="red")
                self.schedule.add(red_waste)
                agent.knowledge["collected_waste"].append(red_waste)
                print(agent, agent.knowledge["collected_waste"])

        elif action == "dispose_waste":
            if not self.is_in_disposal_zone(agent):
                self.move_agent_towards_disposal_zone(agent)
            else:
                if isinstance(agent, GreenAgent):
                    for waste in agent.knowledge["collected_waste"]:
                        self.grid.place_agent(waste, agent.pos)
                    agent.knowledge["collected_waste"].clear()
                    print(agent, agent.knowledge["collected_waste"])
                        
                elif isinstance(agent, YellowAgent):
                    for waste in agent.knowledge["collected_waste"]:
                        self.grid.place_agent(waste, agent.pos)
                    agent.knowledge["collected_waste"].clear()
                    print(agent, agent.knowledge["collected_waste"])
                        
                elif isinstance(agent, RedAgent):
                    agent.knowledge["collected_waste"].clear()
                    print(agent, agent.knowledge["collected_waste"])

    def is_in_disposal_zone(self, agent):
        z_width = self.grid.width // 3
        if isinstance(agent, GreenAgent):
            dx = z_width - 1
        elif isinstance(agent, YellowAgent):
            dx = 2 * z_width - 1
        elif isinstance(agent, RedAgent):
            dx = self.grid.width - 1
        return agent.pos[0] == dx

    def move_robot(self, robot, new_position):
        if not self.is_position_allowed(robot, new_position):
            print(f"Move not allowed for {robot.unique_id} to {new_position}")
            return  
        
        contents = self.grid.get_cell_list_contents(new_position)
        if any(isinstance(c, (GreenAgent, YellowAgent, RedAgent)) for c in contents):
            print(f"Cell {new_position} is occupied")
            return  
        
        self.grid.move_agent(robot, new_position)

    def is_position_allowed(self, robot, position):
        contents = self.grid.get_cell_list_contents(position)
        radioactivity_agents = [a for a in contents if isinstance(a, RadioactivityAgent)]
        if not radioactivity_agents:
            return False

        zone = radioactivity_agents[0].zone    
        if isinstance(robot, GreenAgent) and zone == "z1":
            return True
        elif isinstance(robot, YellowAgent) and (zone == "z1" or zone == "z2"):
            return True
        elif isinstance(robot, RedAgent):
            return True        
        print(f"Move not allowed for {type(robot).__name__} to zone {zone}")
        return False
    
    def move_agent_towards_disposal_zone(self, agent):
        x, y = agent.pos
        z_width = self.grid.width // 3
        if isinstance(agent, GreenAgent):
            dx = z_width - 1
        elif isinstance(agent, YellowAgent):
            dx = 2 * z_width - 1
        else:  # RedAgent
            dx = self.grid.width - 1

        if x < dx:
            new_x = x + 1
        elif x > dx:
            new_x = x - 1
        else:
            new_x = x

        new_y = y

        new_position = (new_x, new_y)
        if self.is_position_allowed(agent, new_position):
            contents = self.grid.get_cell_list_contents(new_position)
            if not any(isinstance(c, (GreenAgent, YellowAgent, RedAgent)) for c in contents):
                self.grid.move_agent(agent, new_position)