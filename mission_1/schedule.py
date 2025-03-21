"""
-------------------------------------------------
Group 1 - Project Name
Created on: 2025-03-11
Authors: Louis LHOTTE, Ambroise MARTIN-ROUVILLE, Edouard SEGUIER
-------------------------------------------------

Description:
This script contains the schedulers
"""


from collections import defaultdict
from mesa.agent import Agent
from typing import Callable, Dict, Iterator, List, Optional, Type, Union
import random

class BaseScheduler:
    """Base scheduler class that serves as the basis for all other scheduler classes."""

    def __init__(self, model):
        """Create a new, empty BaseScheduler."""
        self.model = model
        self.steps = 0
        self.time = 0
        self._agents = {}
        self._agents_dict = {}

    def add(self, agent: Agent) -> None:
        """Add an Agent object to the schedule."""
        self._agents[agent.unique_id] = agent
        agent_class = type(agent)
        # Add agent to dict by class
        if agent_class not in self._agents_dict:
            self._agents_dict[agent_class] = {}
        self._agents_dict[agent_class][agent.unique_id] = agent

    def remove(self, agent: Agent) -> None:
        """Remove the given agent from the schedule."""
        del self._agents[agent.unique_id]

        # Remove from class dict
        agent_class = type(agent)
        del self._agents_dict[agent_class][agent.unique_id]

    def step(self) -> None:
        """Execute the step of all agents, one at a time."""
        for agent in self.agent_buffer():
            agent.step()
        self.steps += 1
        self.time += 1

    def get_agent_count(self) -> int:
        """Return the current number of agents in the queue."""
        return len(self._agents)

    def get_type_count(
        self,
        type_class: Type,
        filter_func: Optional[Callable[[Agent], bool]] = None,
    ) -> int:
        """
        Return the current number of agents of certain type in the queue
        that satisfy the filter function.
        """
        if type_class not in self._agents_dict:
            return 0
        count = 0
        for agent in self._agents_dict[type_class].values():
            if filter_func is None or filter_func(agent):
                count += 1
        return count
    
    @property
    def agents(self) -> List[Agent]:
        """Return a list of all agents in the queue."""
        return list(self._agents.values())

    def agent_buffer(self, shuffled: bool = False) -> Iterator[Agent]:
        """Simple generator that yields an iterator of all agents."""
        agent_list = list(self._agents.values())
        if shuffled:
            random.shuffle(agent_list)
        for agent in agent_list:
            yield agent


class CustomScheduler(BaseScheduler):
    """A scheduler that activates each agent once per step, in random order, without regard to type."""
    def step(self):
        for agent in self.agent_buffer(shuffled=True):
            agent.step()
        self.steps += 1
        self.time += 1


class RandomActivationScheduler(BaseScheduler):
    """
    A scheduler that activates each type of agent in a random order.
    This is equivalent to RandomActivationByType from older Mesa versions.
    """
    
    def __init__(self, model):
        super().__init__(model)
        self.agents_by_type = defaultdict(dict)

    def add(self, agent: Agent) -> None:
        """Add an Agent object to the schedule."""
        super().add(agent)

        # Add to type dictionary
        agent_class = type(agent)
        self.agents_by_type[agent_class][agent.unique_id] = agent

    def remove(self, agent: Agent) -> None:
        """Remove all instances of a given agent from the schedule."""
        super().remove(agent)

        # Remove from type dictionary
        agent_class = type(agent)
        del self.agents_by_type[agent_class][agent.unique_id]

    def step(self) -> None:
        """Executes the step of each agent type in random order."""
        agent_types = list(self.agents_by_type.keys())
        random.shuffle(agent_types)

        for agent_type in agent_types:
            agents = list(self.agents_by_type[agent_type].values())
            random.shuffle(agents)
            for agent in agents:
                agent.step()

        self.steps += 1
        self.time += 1
        
    def get_type_count(
        self,
        type_class: Type[Agent],
        filter_func: Optional[Callable[[Agent], bool]] = None,
    ) -> int:
        """
        Returns the current number of agents of certain type in the queue
        that satisfy the filter function.
        """
        if type_class not in self.agents_by_type:
            return 0
        count = 0
        for agent in self.agents_by_type[type_class].values():
            if filter_func is None or filter_func(agent):
                count += 1
        return count