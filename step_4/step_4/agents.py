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
        self.knowledge = {
            "collected_waste": [],
            "waste_here": False,
            "current_position": None,
            "target_location": None,
            "is_exploring": False,
        }
        self.inbox = []

    def percepts(self):
        contents = self.model.grid.get_cell_list_contents([self.pos])
        waste_here = any(isinstance(c, Waste) and c.waste_type == "green" for c in contents)
        self.knowledge.update({"waste_here": waste_here, "current_position": self.pos})
        if self.knowledge["is_exploring"]:
            self.model.explored_map[self.pos] = True
        
    def deliberate(self, knowledge):
        if knowledge["waste_here"] and len(knowledge["collected_waste"]) < 2:
            return "collect_waste"
        elif len(knowledge["collected_waste"]) == 2:
            return "transform_waste"
        elif len(knowledge["collected_waste"]) == 1 and knowledge["collected_waste"][0].waste_type == "yellow":
            return "dispose_waste"
        else:
            self.knowledge["is_exploring"] = True
            return "move_smartly"

    def do(self, action):
        if action in ["collect_waste", "dispose_waste", "transform_waste"]:
            self.model.perform_action(self, action)
            self.knowledge["is_exploring"] = False
        elif action == "move_randomly":
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
            new_position = self.model.random.choice(possible_steps)
            self.model.move_robot(self, new_position)
        elif action == "move_smartly":
            self.move_smartly()
    
    def move_smartly(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        
        # Filtrer les positions qui sont accessibles
        allowed_positions = [pos for pos in possible_steps if self.model.is_position_allowed(self, pos)]
        
        if not allowed_positions:
            return  # Aucun mouvement possible
        
        # Vérifier si des cellules non explorées sont disponibles
        unexplored_positions = [pos for pos in allowed_positions if not self.model.explored_map.get(pos, False)]
        
        # S'il existe des cellules non explorées, en choisir une au hasard
        if unexplored_positions:
            target_pos = self.model.random.choice(unexplored_positions)
        else:
            # Sinon, choisir aléatoirement parmi toutes les positions autorisées
            target_pos = self.model.random.choice(allowed_positions)
        
        # Vérifier si la position est déjà occupée par un autre robot
        contents = self.model.grid.get_cell_list_contents(target_pos)
        if not any(isinstance(c, (GreenRobot, YellowRobot, RedRobot)) for c in contents):
            self.model.move_robot(self, target_pos)

    def step(self):
        self.percepts()
        action = self.deliberate(self.knowledge)
        self.do(action)

class YellowRobot(Agent):
    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.model = model
        self.pos = None
        self.knowledge = {
            "collected_waste": [],
            "waste_here": False,
            "current_position": None,
            "target_location": None,
            "is_exploring": False,
        }
        self.inbox = []

    def percepts(self):
        contents = self.model.grid.get_cell_list_contents([self.pos])
        waste_here = any(isinstance(c, Waste) and c.waste_type == "yellow" for c in contents)
        self.knowledge.update({"waste_here": waste_here, "current_position": self.pos})
        if self.knowledge["is_exploring"]:
            self.model.explored_map[self.pos] = True
        
    def process_messages(self):
        for message in self.inbox:
            if message.get("type") == "pick_up_waste":
                self.knowledge["target_location"] = message.get("location")
                self.knowledge["is_exploring"] = False  # Arrêter l'exploration quand un message est reçu
        self.inbox.clear()

    def deliberate(self, knowledge):
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
            # Commencer l'exploration à la recherche de déchets
            self.knowledge["is_exploring"] = True
            return "move_smartly"

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

    def move_smartly(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        
        # Filtrer les positions qui sont accessibles
        allowed_positions = [pos for pos in possible_steps if self.model.is_position_allowed(self, pos)]
        
        if not allowed_positions:
            return  # Aucun mouvement possible
        
        # Vérifier si des cellules non explorées sont disponibles
        unexplored_positions = [pos for pos in allowed_positions if not self.model.explored_map.get(pos, False)]
        
        # S'il existe des cellules non explorées, en choisir une au hasard
        if unexplored_positions:
            target_pos = self.model.random.choice(unexplored_positions)
        else:
            # Sinon, choisir aléatoirement parmi toutes les positions autorisées
            target_pos = self.model.random.choice(allowed_positions)
        
        # Vérifier si la position est déjà occupée par un autre robot
        contents = self.model.grid.get_cell_list_contents(target_pos)
        if not any(isinstance(c, (GreenRobot, YellowRobot, RedRobot)) for c in contents):
            self.model.move_robot(self, target_pos)

    def do(self, action):
        if action in ["collect_waste", "dispose_waste", "transform_waste"]:
            self.model.perform_action(self, action)
            # Fin de l'exploration quand une action est effectuée
            self.knowledge["is_exploring"] = False
        elif action == "move_randomly":
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
            new_position = self.model.random.choice(possible_steps)
            self.model.move_robot(self, new_position)
        elif action == "move_to_target":
            self.move_towards_target()
        elif action == "move_smartly":
            self.move_smartly()

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
            "is_exploring": False,
        }
        self.inbox = []

    def percepts(self):
        contents = self.model.grid.get_cell_list_contents([self.pos])
        waste_here = any(isinstance(c, Waste) and c.waste_type == "red" for c in contents)
        self.knowledge.update({"waste_here": waste_here, "current_position": self.pos})
        if self.knowledge["is_exploring"]:
            self.model.explored_map[self.pos] = True
        
    def process_messages(self):
        for message in self.inbox:
            if message.get("type") == "pick_up_waste":
                self.knowledge["target_location"] = message.get("location")
                self.knowledge["is_exploring"] = False  # Arrêter l'exploration quand un message est reçu
        self.inbox.clear()

    def deliberate(self, knowledge):
        if knowledge.get("target_location") is not None and knowledge["current_position"] != knowledge["target_location"]:
            return "move_to_target"
        if knowledge["waste_here"] and len(knowledge["collected_waste"]) == 0:
            return "collect_waste"
        elif len(knowledge["collected_waste"]) == 1:
            return "dispose_waste"
        else:
            # Commencer l'exploration à la recherche de déchets
            self.knowledge["is_exploring"] = True
            return "move_smartly"

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

    def move_smartly(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        
        # Prendre parmi les positions qui sont accessibles
        allowed_positions = [pos for pos in possible_steps if self.model.is_position_allowed(self, pos)]
        
        if not allowed_positions:
            return  # Aucun mouvement possible
        
        # Vérifier si des cellules non explorées sont disponibles
        unexplored_positions = [pos for pos in allowed_positions if not self.model.explored_map.get(pos, False)]
        
        # S'il existe des cellules non explorées, en choisir une au hasard
        if unexplored_positions:
            target_pos = self.model.random.choice(unexplored_positions)
        else:
            # Sinon, choisir aléatoirement parmi toutes les positions autorisées
            target_pos = self.model.random.choice(allowed_positions)
        
        # Vérifier si la position est déjà occupée par un autre robot
        contents = self.model.grid.get_cell_list_contents(target_pos)
        if not any(isinstance(c, (GreenRobot, YellowRobot, RedRobot)) for c in contents):
            self.model.move_robot(self, target_pos)

    def do(self, action):
        if action in ["collect_waste", "dispose_waste"]:
            self.model.perform_action(self, action)
            # Fin de l'exploration quand une action est effectuée
            self.knowledge["is_exploring"] = False
        elif action == "move_randomly":
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
            new_position = self.model.random.choice(possible_steps)
            self.model.move_robot(self, new_position)
        elif action == "move_to_target":
            self.move_towards_target()
        elif action == "move_smartly":
            self.move_smartly()

    def step(self):
        self.process_messages()
        self.percepts()
        action = self.deliberate(self.knowledge)
        self.do(action)