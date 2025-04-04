"""
-------------------------------------------------
Group 1 - Project Name
Created on: 2025-03-11
Authors: Louis LHOTTE, Ambroise MARTIN-ROUVILLE, Edouard SEGUIER
-------------------------------------------------

Description:
This script depicts the different zones, their waste and radioactivity.
"""

from mesa import Agent
import random

class Radioactivity(Agent):
    """A non-behavioral agent representing the level of radioactivity in a zone."""
    def __init__(self, unique_id, model, zone):
        self.unique_id = unique_id
        self.model = model
        self.pos = None  
        self.zone = zone
        self.radioactivity = self.assign_radioactivity_level(zone)
        
    def assign_radioactivity_level(self, zone):
        if zone == "z1":
            return random.uniform(0, 0.33)
        elif zone == "z2":
            return random.uniform(0.33, 0.66)
        else:  # zone "z3"
            return random.uniform(0.66, 1)

class WasteDisposalZone(Agent):
    """A non-behavioral agent indicating the waste disposal zone."""
    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.model = model
        self.pos = None  # Initialize pos attribute to None
        self.is_disposal_zone = True

class Waste(Agent):
    """Represents waste objects."""
    def __init__(self, unique_id, model, waste_type):
        self.unique_id = unique_id
        self.model = model
        self.pos = None  # Initialize pos attribute to None
        self.waste_type = waste_type  # green, yellow, red