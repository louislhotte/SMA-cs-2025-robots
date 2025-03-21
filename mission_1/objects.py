
from mesa import Agent
import random

class Radioactivity(Agent):
    """A non-behavioral agent representing the level of radioactivity in a zone."""
    def __init__(self, unique_id, model, zone):
        # Fixed initialization for Mesa 3.1.4
        self.unique_id = unique_id
        self.model = model
        self.pos = None  # Initialize pos attribute to None
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
        # Fixed initialization for Mesa 3.1.4
        self.unique_id = unique_id
        self.model = model
        self.pos = None  # Initialize pos attribute to None
        # Assuming a value to identify this as a disposal zone, if needed.
        self.is_disposal_zone = True

class Waste(Agent):
    """Represents waste objects."""
    def __init__(self, unique_id, model, waste_type):
        # Fixed initialization for Mesa 3.1.4
        self.unique_id = unique_id
        self.model = model
        self.pos = None  # Initialize pos attribute to None
        self.waste_type = waste_type  # green, yellow, red