"""
-------------------------------------------------
Group 1 - Project Name
Created on: 2025-03-11
Authors: Louis LHOTTE, Ambroise MARTIN-ROUVILLE, Edouard SEGUIER
-------------------------------------------------

Description:
This script defines the Radioactive and robot agents.
Now, robots can communicate: when a transformation occurs,
the transforming robot sends a message to the closest agent of the next type.
"""

from mesa import Agent
from objects import Waste

class GreenRobot(Agent):
    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.model = model
        self.pos = None
        # Extend knowledge to include target_location (not used by green)
        self.knowledge = {
            "collected_waste": [],
            "waste_here": False,
            "current_position": None,
            "target_location": None,
        }
        # Inbox for receiving messages
        self.inbox = []

    def percepts(self):
        contents = self.model.grid.get_cell_list_contents([self.pos])
        waste_here = any(isinstance(c, Waste) and c.waste_type == "green" for c in contents)
        self.knowledge.update({"waste_here": waste_here, "current_position": self.pos})
        
    def deliberate(self, knowledge):
        # GreenRobot does not process messages in this example.
        if knowledge["waste_here"] and len(knowledge["collected_waste"]) < 2:
            return "collect_waste"
        elif len(knowledge["collected_waste"]) == 2:
            return "transform_waste"
        elif len(knowledge["collected_waste"]) == 1 and knowledge["collected_waste"][0].waste_type == "yellow":
            return "dispose_waste"
        else:
            return "move_randomly"

    def do(self, action):
        if action in ["collect_waste", "dispose_waste", "transform_waste"]:
            self.model.perform_action(self, action)
        elif action == "move_randomly":
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
            new_position = self.model.random.choice(possible_steps)
            self.model.move_robot(self, new_position)

    def step(self):
        self.percepts()
        action = self.deliberate(self.knowledge)
        self.do(action)

class YellowRobot(Agent):
    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.model = model
        self.pos = None
        # Extend knowledge to include a target for incoming messages.
        self.knowledge = {
            "collected_waste": [],
            "waste_here": False,
            "current_position": None,
            "target_location": None,
        }
        self.inbox = []

    def percepts(self):
        contents = self.model.grid.get_cell_list_contents([self.pos])
        waste_here = any(isinstance(c, Waste) and c.waste_type == "yellow" for c in contents)
        self.knowledge.update({"waste_here": waste_here, "current_position": self.pos})
        
    def process_messages(self):
        # Process any pick_up messages and set a target location accordingly.
        for message in self.inbox:
            if message.get("type") == "pick_up_waste":
                self.knowledge["target_location"] = message.get("location")
        self.inbox.clear()

    def deliberate(self, knowledge):
        # If a target is set and not yet reached, move toward it.
        if knowledge.get("target_location") is not None and knowledge["current_position"] != knowledge["target_location"]:
            return "move_to_target"
        # Otherwise, follow normal behavior.
        if knowledge["waste_here"] and len(knowledge["collected_waste"]) < 2:
            return "collect_waste"
        elif len(knowledge["collected_waste"]) == 2:
            return "transform_waste"
        elif len(knowledge["collected_waste"]) == 1 and knowledge["collected_waste"][0].waste_type == "red":
            return "dispose_waste"
        else:
            return "move_randomly"

    def move_towards_target(self):
        target = self.knowledge["target_location"]
        if target is None:
            return
        x, y = self.pos
        tx, ty = target
        # Move one step closer in x and/or y direction
        if x < tx:
            new_x = x + 1
        elif x > tx:
            new_x = x - 1
        else:
            new_x = x
        if y < ty:
            new_y = y + 1
        elif y > ty:
            new_y = y - 1
        else:
            new_y = y
        new_position = (new_x, new_y)
        self.model.move_robot(self, new_position)
        # Clear target if reached
        if new_position == target:
            self.knowledge["target_location"] = None

    def do(self, action):
        if action in ["collect_waste", "dispose_waste", "transform_waste"]:
            self.model.perform_action(self, action)
        elif action == "move_randomly":
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
            new_position = self.model.random.choice(possible_steps)
            self.model.move_robot(self, new_position)
        elif action == "move_to_target":
            self.move_towards_target()

    def step(self):
        self.process_messages()
        self.percepts()
        action = self.deliberate(self.knowledge)
        self.do(action)

class RedRobot(Agent):
    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.model = model
        self.pos = None
        # Extend knowledge for target messages.
        self.knowledge = {
            "collected_waste": [],
            "waste_here": False,
            "current_position": None,
            "target_location": None,
        }
        self.inbox = []

    def percepts(self):
        contents = self.model.grid.get_cell_list_contents([self.pos])
        waste_here = any(isinstance(c, Waste) and c.waste_type == "red" for c in contents)
        self.knowledge.update({"waste_here": waste_here, "current_position": self.pos})
        
    def process_messages(self):
        for message in self.inbox:
            if message.get("type") == "pick_up_waste":
                self.knowledge["target_location"] = message.get("location")
        self.inbox.clear()

    def deliberate(self, knowledge):
        if knowledge.get("target_location") is not None and knowledge["current_position"] != knowledge["target_location"]:
            return "move_to_target"
        if knowledge["waste_here"] and len(knowledge["collected_waste"]) == 0:
            return "collect_waste"
        elif len(knowledge["collected_waste"]) == 1:
            return "dispose_waste"
        else:
            return "move_randomly"

    def move_towards_target(self):
        target = self.knowledge["target_location"]
        if target is None:
            return
        x, y = self.pos
        tx, ty = target
        if x < tx:
            new_x = x + 1
        elif x > tx:
            new_x = x - 1
        else:
            new_x = x
        if y < ty:
            new_y = y + 1
        elif y > ty:
            new_y = y - 1
        else:
            new_y = y
        new_position = (new_x, new_y)
        self.model.move_robot(self, new_position)
        if new_position == target:
            self.knowledge["target_location"] = None

    def do(self, action):
        if action in ["collect_waste", "dispose_waste"]:
            self.model.perform_action(self, action)
        elif action == "move_randomly":
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
            new_position = self.model.random.choice(possible_steps)
            self.model.move_robot(self, new_position)
        elif action == "move_to_target":
            self.move_towards_target()

    def step(self):
        self.process_messages()
        self.percepts()
        action = self.deliberate(self.knowledge)
        self.do(action)
