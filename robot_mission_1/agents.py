"""
-------------------------------------------------
Group 1 - Project Name
Created on: 2025-03-11
Authors: Louis LHOTTE, Ambroise MARTIN-ROUVILLE, Edouard SEGUIER
-------------------------------------------------

Description:
This script defines the Radioactive and green agents
"""

# Your Python code starts below
from mesa import Agent
from objects import Waste
import random


def is_in_disposal_zone(self):
        z_width = self.model.grid.width // 3
        if isinstance(self, GreenAgent):
            dx = z_width - 1   # Disposal zone for GreenAgent is at the end of z1
        elif isinstance(self, YellowAgent):
            dx = 2 * z_width - 1
        elif isinstance(self, RedAgent):
            dx = self.grid.width - 1
        # Check if the agent is at the disposal zone
        return self.pos[0] == dx

class GreenAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.knowledge = {"collected_waste": [], "waste_here": False, "current_position": None}

    def percepts(self):
        """Gather information from the environment."""
        contents = self.model.grid.get_cell_list_contents([self.pos])
        waste_here = any(isinstance(c, Waste) and c.waste_type == "green" for c in contents)
        self.knowledge.update({"waste_here": waste_here, "current_position": self.pos})

    def deliberate(self, knowledge):
        """Decide on an action based on the current knowledge."""
        # If the Agent is on waste and hasn't collected 2 wastes yet, collect more waste.
        if knowledge["waste_here"] and len(knowledge["collected_waste"]) < 2 :
            if knowledge["collected_waste"] == []:
                return "collect_waste"
            elif knowledge["collected_waste"][0].waste_type == "yellow":
                return "dispose_waste"
            else:       
                return "collect_waste"
        # If the Agent has collected 2 green wastes, it should transform them into yellow waste.
        elif len(knowledge["collected_waste"]) == 2:
            return "transform_waste"
        # If the Agent has transformed the waste (implying it has 1 yellow waste), it should dispose of the waste.
        elif len(knowledge["collected_waste"]) == 1 and knowledge["collected_waste"][0].waste_type == "yellow":
            return "dispose_waste"
        # Otherwise, move randomly.
        else:
            return "move_randomly"
        
    def move_to_least_visited(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        allowed_neighbors = [pos for pos in neighbors if self.model.is_position_allowed(self, pos)]
        # Choose the neighbor with the least pheromones
        next_move = min(allowed_neighbors, key=lambda pos: (self.model.pheromone_levels['green'][pos], random.random()))
        return next_move

    def deposit_pheromone(self):
        x, y = self.pos
        self.model.pheromone_levels['green'][(x, y)] += 1  # Only update green pheromone levels

    def do(self, action):
        """Perform an action and update the environment and knowledge accordingly."""
        if action == "collect_waste" or action == "dispose_waste" or action == "transform_waste":
            self.model.perform_action(self, action)
        elif action == "move_randomly":
            #possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
            new_position = self.move_to_least_visited()
            self.model.move_Agent(self, new_position)
            self.deposit_pheromone()

    def step(self):
        percepts = self.percepts()
        action = self.deliberate(self.knowledge)
        self.do(action)

class YellowAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.knowledge = {"collected_waste": [], "waste_here": False, "current_position": None}

    def percepts(self):
        """Gather information from the environment."""
        contents = self.model.grid.get_cell_list_contents([self.pos])
        waste_here = any(isinstance(c, Waste) and c.waste_type == "yellow" for c in contents)
        self.knowledge.update({"waste_here": waste_here, "current_position": self.pos})

    def deliberate(self, knowledge):
        """Decide on an action based on the current knowledge."""
        # If the Agent is on waste and hasn't collected 2 wastes yet, collect more waste.
        if knowledge["waste_here"] and len(knowledge["collected_waste"]) < 2 :
            if knowledge["collected_waste"] == []:
                return "collect_waste"
            elif knowledge["collected_waste"][0].waste_type == "red":
                return "dispose_waste"
            else:
                return "collect_waste"
        # If the Agent has collected 2 green wastes, it should transform them into yellow waste.
        elif len(knowledge["collected_waste"]) == 2:
            return "transform_waste"
        # If the Agent has transformed the waste (implying it has 1 yellow waste), it should dispose of the waste.
        elif len(knowledge["collected_waste"]) == 1 and knowledge["collected_waste"][0].waste_type == "red":
            return "dispose_waste"
        # Otherwise, move randomly.
        else:
            return "move_randomly"
        
    def move_to_least_visited(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        allowed_neighbors = [pos for pos in neighbors if self.model.is_position_allowed(self, pos)]
        # Choose the neighbor with the least pheromones
        next_move = min(allowed_neighbors, key=lambda pos: (self.model.pheromone_levels['yellow'][pos], random.random()))
        return next_move

    def deposit_pheromone(self):
        x, y = self.pos
        self.model.pheromone_levels['yellow'][(x, y)] += 1  # Only update yellow pheromone levels

    def do(self, action):
        """Perform an action and update the environment and knowledge accordingly."""
        if action == "collect_waste" or action == "dispose_waste" or action == "transform_waste":
            self.model.perform_action(self, action)
        elif action == "move_randomly":
            new_position = self.move_to_least_visited()
            self.model.move_Agent(self, new_position)
            self.deposit_pheromone()


    def step(self):
        percepts = self.percepts()
        action = self.deliberate(self.knowledge)
        self.do(action)

class RedAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.knowledge = {"collected_waste": [], "waste_here": False, "current_position": None}

    def percepts(self):
        """Gather information from the environment."""
        contents = self.model.grid.get_cell_list_contents([self.pos])
        waste_here = any(isinstance(c, Waste) and c.waste_type == "red" for c in contents)
        self.knowledge.update({"waste_here": waste_here, "current_position": self.pos})

    def deliberate(self, knowledge):
        """Decide on an action based on the current knowledge."""
        if knowledge["waste_here"] and len(knowledge["collected_waste"]) == 0:
            return "collect_waste" 
        elif len(knowledge["collected_waste"]) == 1:
            return "dispose_waste"
        # Otherwise, move randomly.
        else:
            return "move_randomly"
        
    def move_to_least_visited(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        # Choose the neighbor with the least pheromones
        next_move = min(neighbors, key=lambda pos: (self.model.pheromone_levels['red'][pos], random.random()))
        return next_move

    def deposit_pheromone(self):
        x, y = self.pos
        self.model.pheromone_levels['red'][(x, y)] += 1  # Only update red pheromone levels

    def do(self, action):
        """Perform an action and update the environment and knowledge accordingly."""
        if action == "collect_waste" or action == "dispose_waste" :
            self.model.perform_action(self, action)
        elif action == "move_randomly":
            new_position = self.move_to_least_visited()
            self.model.move_Agent(self, new_position)
            self.deposit_pheromone()

    def step(self):
        percepts = self.percepts()
        action = self.deliberate(self.knowledge)
        self.do(action)

import random

class RandomActivationScheduler:
    def __init__(self, model):
        self.model = model
        self._agents = {}
        self.steps = 0
        self.time = 0

    def add(self, agent):
        self._agents[agent.unique_id] = agent

    def remove(self, agent):
        if agent.unique_id in self._agents:
            del self._agents[agent.unique_id]

    def step(self):
        agent_keys = list(self._agents.keys())
        random.shuffle(agent_keys)
        for key in agent_keys:
            agent = self._agents[key]
            agent.step()
        self.steps += 1
        self.time += 1

    def get_agent_count(self):
        return len(self._agents)

    def get_type_count(self, agent_type):
        c = 0
        for agent in self._agents.values():
            if isinstance(agent, agent_type):
                c += 1
        return c
