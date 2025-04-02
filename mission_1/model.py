"""
-------------------------------------------------
Group 1 - Project Project
Created on: 2025-03-11
Authors: Louis LHOTTE, Ambroise MARTIN-ROUVILLE, Edouard SEGUIER
-------------------------------------------------

Description:
This script sets up the simulation, places agents and wastes,
and now also handles communication between robots.
"""

from mesa import Model, DataCollector
from mesa.space import MultiGrid
import random as py_random
from agents import GreenRobot, YellowRobot, RedRobot  
from objects import Waste, WasteDisposalZone, Radioactivity 
from schedule import RandomActivationScheduler

class RobotMission(Model):
    def __init__(self, width, height, initial_green_waste, initial_yellow_waste, initial_red_waste, nb_yellow_agent, nb_green_agent, nb_red_agent):
        super().__init__() 
        self.random = py_random.Random()
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivationScheduler(self)
        self.initial_green_waste = initial_green_waste
        self.initial_yellow_waste = initial_yellow_waste
        self.initial_red_waste = initial_red_waste
        self.nb_yellow_agent = nb_yellow_agent
        self.nb_green_agent = nb_green_agent
        self.nb_red_agent = nb_red_agent

        self.explored_map = {}
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                self.explored_map[(x, y)] = False
        
        self.pheromone_decay_rate = 0.1 

        l = self.grid.width // 3
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if x < l:
                    zone = "z1"
                elif x < 2 * l:
                    zone = "z2"
                else:
                    zone = "z3"
                radioactivity_agent = Radioactivity(self.schedule.get_agent_count(), self, zone)
                self.grid.place_agent(radioactivity_agent, (x, y))
                self.schedule.add(radioactivity_agent)
                
        z_width = l
        height = self.grid.height
        self.datacollector = DataCollector({
            "Waste": lambda m: m.schedule.get_type_count(Waste),
        })

 

        def find_empty_cell(x_start, x_end, height, grid):
            while True:
                x = self.random.randrange(x_start, x_end)
                y = self.random.randrange(0, height)
                cell_contents = grid.get_cell_list_contents((x, y))
                if not any(isinstance(agent, (GreenRobot, YellowRobot, RedRobot)) for agent in cell_contents):
                    return x, y

        for _ in range(self.nb_green_agent):
            x, y = find_empty_cell(0, z_width - 1, height, self.grid)
            robot = GreenRobot(self.schedule.get_agent_count(), self)
            self.schedule.add(robot)
            self.grid.place_agent(robot, (x, y))

        for _ in range(self.nb_yellow_agent):
            x, y = find_empty_cell(0, 2 * z_width - 1, height, self.grid)
            robot = YellowRobot(self.schedule.get_agent_count(), self)
            self.schedule.add(robot)
            self.grid.place_agent(robot, (x, y))

        for _ in range(self.nb_red_agent):
            x, y = find_empty_cell(0, self.grid.width - 1, height, self.grid)
            robot = RedRobot(self.schedule.get_agent_count(), self)
            self.schedule.add(robot)
            self.grid.place_agent(robot, (x, y))
            
        for _ in range(initial_green_waste):
            self.place_waste_in_zone("green", 0, z_width - 1, height)
        for _ in range(initial_yellow_waste):
            self.place_waste_in_zone("yellow", z_width, 2 * z_width - 1, height)
        for _ in range(initial_red_waste):
            self.place_waste_in_zone("red", 2 * z_width, width - 1, height)
            
        for y in range(height):
            dz1_pos = (z_width - 1, y)
            dz1_agent = WasteDisposalZone(self.schedule.get_agent_count(), self)
            self.grid.place_agent(dz1_agent, dz1_pos)
            self.schedule.add(dz1_agent)

            dz2_pos = (2 * z_width - 1, y)
            dz2_agent = WasteDisposalZone(self.schedule.get_agent_count(), self)
            self.grid.place_agent(dz2_agent, dz2_pos)
            self.schedule.add(dz2_agent)

            dz3_pos = (self.grid.width - 1, y)
            dz3_agent = WasteDisposalZone(self.schedule.get_agent_count(), self)
            self.grid.place_agent(dz3_agent, dz3_pos)
            self.schedule.add(dz3_agent)
    
    def reset_old_explorations(self):
        "Réinitialise périodiquement certaines cellules explorées pour permettre la redécouverte."
        if self.schedule.steps % 30 == 0:  # Tous les 20 pas de simulation
            for pos in list(self.explored_map.keys()):                    # Une chance basée sur le taux de déclin pour réinitialiser une cellule explorée
                if self.explored_map[pos] and self.random.random() < self.pheromone_decay_rate:
                    self.explored_map[pos] = False

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        self.reset_old_explorations()

    def place_waste_in_zone(self, waste_type, x_start, x_end, height):
        waste = Waste(self.schedule.get_agent_count(), self, waste_type=waste_type)
        while True:
            pos = (self.random.randrange(x_start, x_end), self.random.randrange(height))
            self.grid.place_agent(waste, pos)
            self.schedule.add(waste)
            break

    def perform_action(self, agent, action):
        if action == "collect_waste":
            contents = self.grid.get_cell_list_contents(agent.pos)
            target_waste_type = "green" if isinstance(agent, GreenRobot) else ("yellow" if isinstance(agent, YellowRobot) else "red")
            for content in contents:
                if isinstance(content, Waste) and content.waste_type == target_waste_type and len(agent.knowledge["collected_waste"]) < 2:
                    agent.knowledge["collected_waste"].append(content)
                    self.grid.remove_agent(content)
                    self.schedule.remove(content)
                    print(f"{agent} collected {content}")
                    break  
        elif action == "transform_waste":
            # For GreenRobot: transform two green wastes into yellow waste and notify a YellowRobot.
            if isinstance(agent, GreenRobot) and len(agent.knowledge["collected_waste"]) == 2:
                agent.knowledge["collected_waste"].clear()
                yellow_waste = Waste(self.schedule.get_agent_count(), self, waste_type="yellow")
                self.grid.place_agent(yellow_waste, agent.pos)
                self.schedule.add(yellow_waste)
                print(f"{agent} transformed green waste into yellow waste: {yellow_waste}")
                closest_yellow = self.get_closest_agent(agent.pos, YellowRobot)
                if closest_yellow is not None:
                    message = {"type": "pick_up_waste", "waste_id": yellow_waste.unique_id, "location": agent.pos}
                    self.send_message(closest_yellow, message)
            # For YellowRobot: transform two yellow wastes into red waste and notify a RedRobot.
            if isinstance(agent, YellowRobot) and len(agent.knowledge["collected_waste"]) == 2:
                agent.knowledge["collected_waste"].clear()
                red_waste = Waste(self.schedule.get_agent_count(), self, waste_type="red")
                self.grid.place_agent(red_waste, agent.pos)
                self.schedule.add(red_waste)
                print(f"{agent} transformed yellow waste into red waste: {red_waste}")
                closest_red = self.get_closest_agent(agent.pos, RedRobot)
                if closest_red is not None:
                    message = {"type": "pick_up_waste", "waste_id": red_waste.unique_id, "location": agent.pos}
                    self.send_message(closest_red, message)
        elif action == "dispose_waste":
            if not self.is_in_disposal_zone(agent):
                self.move_agent_towards_disposal_zone(agent)
            else:
                if isinstance(agent, GreenRobot):
                    for waste in agent.knowledge["collected_waste"]:
                        self.grid.place_agent(waste, agent.pos)
                        agent.knowledge["collected_waste"].clear()
                        print(f"{agent} disposed yellow waste")
                elif isinstance(agent, YellowRobot): 
                    for waste in agent.knowledge["collected_waste"]:
                        self.grid.place_agent(waste, agent.pos)
                        agent.knowledge["collected_waste"].clear()
                        print(f"{agent} disposed red waste")
                elif isinstance(agent, RedRobot):
                    agent.knowledge["collected_waste"].clear()
                    print(f"{agent} disposed red waste")

    def is_in_disposal_zone(self, agent):
        z_width = self.grid.width // 3
        if isinstance(agent, GreenRobot):
            dx = z_width - 1
        elif isinstance(agent, YellowRobot):
            dx = 2 * z_width - 1
        elif isinstance(agent, RedRobot):
            dx = self.grid.width - 1
        return agent.pos[0] == dx

    def move_robot(self, robot, new_position):
        if not self.is_position_allowed(robot, new_position):
            return
        contents = self.grid.get_cell_list_contents(new_position)
        if any(isinstance(c, (GreenRobot, YellowRobot, RedRobot)) for c in contents):
            return
        self.grid.move_agent(robot, new_position)

    def is_position_allowed(self, robot, position):
        contents = self.grid.get_cell_list_contents(position)
        radioactivity_agents = [agent for agent in contents if hasattr(agent, "zone")]
        if not radioactivity_agents:
            return False
        zone = radioactivity_agents[0].zone      
        if isinstance(robot, GreenRobot) and zone == "z1":
            return True
        elif isinstance(robot, YellowRobot) and (zone == "z1" or zone == "z2"):
            return True
        elif isinstance(robot, RedRobot):
            return True        
        return False
    
    def move_agent_towards_disposal_zone(self, agent):
        x, y = agent.pos
        z_width = self.grid.width // 3
        if isinstance(agent, GreenRobot):
            dx = z_width - 1
        elif isinstance(agent, YellowRobot):
            dx = 2 * z_width - 1
        elif isinstance(agent, RedRobot):
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
            if not any(isinstance(c, (GreenRobot, YellowRobot, RedRobot)) for c in contents):
                self.grid.move_agent(agent, new_position)

    # --- New communication helper methods ---

    def get_closest_agent(self, pos, agent_class):
        min_distance = None
        closest_agent = None
        for agent in self.schedule.agents:
            if isinstance(agent, agent_class) and agent.pos is not None:
                distance = abs(agent.pos[0] - pos[0]) + abs(agent.pos[1] - pos[1])
                if min_distance is None or distance < min_distance:
                    min_distance = distance
                    closest_agent = agent
        return closest_agent

    def send_message(self, recipient, message):
        if hasattr(recipient, "inbox"):
            recipient.inbox.append(message)
            print(f"Message sent to agent {recipient.unique_id}: {message}")
