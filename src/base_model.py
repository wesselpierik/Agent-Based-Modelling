import mesa
import mesa.space
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import target
import police
import thief
from heatmap import HeatmapTile
import numpy as np
import random


class BaseModel(mesa.Model):
    def __init__(
        self,
        width: int = 50,
        height: int = 50,
        police_vision_radius: int = 8,
        thief_vision_radius: int = 3,
        police_attentiveness: float = 0.8,
        n_police: int = 5,
        decay_attentiveness: float = 0.1,
        decay_riskiness: float = 0.5,
        increase_attentiveness: float = 0.5,
        increase_riskiness: float = 0.05,
        loot: float = 5,
        fine: float = 2,
        **kwargs,
    ) -> None:
        """
        Initializes the model

        Args:
            width:                  width of the grid
            height:                 height of the grid
            police_vision_radius:   radius of cells police can see
            thief_vision_radius:    radius of cells a thief can see
            police_attentiveness:   attentiveness of police agents
            n_police:               amount of police agents
            decay_attentiveness:    The factor at which targets will
                                    reduce their attentiveness
                                    (new_attentiveness = old_attentiveness
                                    - decay_factor)
            decay_riskiness:        The factor at which thieves will reduce
                                    their riskiness if they get caught
                                    (new_riskiness = old_riskiness
                                    * decay_factor)
            increase_attentiveness: The factor at which targets will increase
                                    their attentiveness if they get robbed
                                    (new_attentiveness = old_attentiveness
                                    + increase_factor)
            increase_riskiness:     The factor at which thieves will increase
                                    their riskiness if they are successful
                                    or do not try
                                    (new_riskiness = old_riskiness
                                    * increase_factor)
            loot:                   The multiplicative reward for thieves
            fine:                   The multiplicative fine for thieves
        """
        super().__init__()
        # set all parameters
        self.height = height
        self.width = width
        self.n_thieves = 5
        self.n_targets = 1500
        self.n_police = n_police

        self._police_vision_radius = police_vision_radius
        self._thief_vision_radius = thief_vision_radius
        self._target_vision_radius = 1

        self._loot = loot
        self._fine = fine

        self._police_attentiveness = police_attentiveness

        self._decay_attentiveness = decay_attentiveness
        self._decay_riskiness = decay_riskiness
        self._increase_attentiveness = increase_attentiveness
        self._increase_riskiness = increase_riskiness

        self.schedule_Police = RandomActivation(self)
        self.schedule_Target = RandomActivation(self)
        self.schedule_Thief = RandomActivation(self)

        self.schedule = RandomActivation(self)

        self.grid = mesa.space.MultiGrid(width, height, False)

        # Collect data for plots in server.py
        self.datacollector = DataCollector(
            {
                "Attempts": lambda m: sum(
                    agent.attempts for agent in m._agents if type(agent) is thief.Thief
                ),
                "Succesful": lambda m: (
                    sum(
                        agent.succesful_steals
                        for agent in m._agents
                        if type(agent) is thief.Thief
                    )
                ),
                "Avg Attentiveness": lambda m: sum(
                    agent.get_attentiveness()
                    for agent in m._agents
                    if type(agent) is target.Target
                )
                / self.n_targets,
                "Avg Riskiness": lambda m: sum(
                    agent.get_riskiness()
                    for agent in m._agents
                    if type(agent) is thief.Thief
                )
                / self.n_thieves,
            }
        )

        self._n_agents = 0
        self._agents = []
        self.crime_heatmap = np.zeros((width, height))

        # Create initial population of agents
        self.init_population_police_patrol(self.n_police)
        self.init_population(thief.Thief, self.n_thieves)
        self.init_population(target.Target, self.n_targets)

        self.running = True
        self.datacollector.collect(self)

    def add_agent(self, agent_type: type, pos: tuple[int, int]) -> None:
        """
        Instantiates a specific type of agent

        Args:
            agent_type: Class of agent (Police, Thief, Target).
            pos:        Coordinate pair (x, y) target placement.

        Raises ValueError if an unexpected class object is passed.
        """
        match agent_type:
            case police.Police:
                vision_radius = self._police_vision_radius
            case target.Target:
                vision_radius = self._target_vision_radius
            case thief.Thief:
                vision_radius = self._thief_vision_radius
            case _:
                raise ValueError(
                    f"Trying to add an unknown class of agent type {agent_type}"
                )

        # Create new agent
        new_agent = agent_type(self._n_agents, self, pos, vision_radius)

        # Place the agent in the grid
        self.grid.place_agent(new_agent, pos)

        # Add the agent to the model
        self._agents.append(new_agent)

        # Update the household value
        self._n_agents = len(self._agents)

        self.schedule.add(new_agent)
        getattr(self, f"schedule_{agent_type.__name__}").add(new_agent)

    def remove_agent(self, agent) -> None:
        """
        Removes agent from the grid, model and schedule

        Args:
            agent: The agent to remove
        """
        self.grid.remove_agent(agent)
        self._agents.remove(agent)
        self.schedule.remove(agent)
        getattr(self, f"schedule_{type(agent).__name__}").remove(agent)

        # Update household values
        self._n_agents = len(self._agents)

    def init_population(self, agent_type: type, n: int) -> None:
        """
        Adds the desired amount of agents to the grid

        Args:
            agent_type: Class of agent to add.
            n:          Amount of agents to add.
        """
        agents_spawned = 0
        while agents_spawned < n:
            i = random.randint(0, self.grid.width - 1)
            j = random.randint(0, self.grid.height - 1)

            if (i, j) in self.grid.empties:
                self.add_agent(agent_type, (i, j))
                agents_spawned += 1  # Only count successful spawns!

    def init_population_police_patrol(self, n: int) -> float:
        """
        Adds the desired amount of police to the grid with a certain
        amount of horizontal space between them

        Args:
            n: Amount of patrolling police officers to add.
        """
        i_coordinates = np.linspace(5, self.grid.width - 6, n, dtype=int)
        for k in range(n):
            target_i = int(i_coordinates[k])
            spawned = False
            while not spawned:
                target_j = random.randint(0, self.grid.height - 1)
                if (target_i, target_j) in self.grid.empties:
                    self.add_agent(police.Police, (target_i, target_j))
                    spawned = True

    def get_local_business(self, pos: tuple[int, int]) -> float:
        """
        Calculates the local crowd density (business) within a Moore
        neighborhood of radius 10. Not used in the code anymore.

        Args:
            pos: cell location of the checking agent.

        Returns:
            float: Local population crowding density
        """
        local_cells = self.grid.get_neighborhood(
            pos, moore=True, include_center=True, radius=10
        )
        local_contents = self.grid.get_cell_list_contents(local_cells)
        local_people = [
            agent for agent in local_contents if not isinstance(agent, HeatmapTile)
        ]
        amount_of_people_local = len(local_people)
        local_grid_size = len(local_cells)
        return amount_of_people_local / local_grid_size

    def get_police_attentiveness(self) -> float:
        return self._police_attentiveness

    def get_successful_thefts(self) -> int:
        return self.datacollector.get_model_vars_dataframe()["Succesful"]

    def get_caught_thieves(self) -> int:
        return (
            self.datacollector.get_model_vars_dataframe()["Attempts"]
            - self.datacollector.get_model_vars_dataframe()["Succesful"]
        )

    def get_loot(self) -> float:
        return self._loot

    def get_fine(self) -> float:
        return self._fine

    def get_police_vision_radius(self) -> int:
        return self._police_vision_radius

    def get_thief_vision_radius(self) -> int:
        return self._thief_vision_radius

    def get_target_vision_radius(self) -> int:
        return self._target_vision_radius

    def get_decay_attentiveness_factor(self) -> float:
        return self._decay_attentiveness

    def get_decay_riskiness_factor(self) -> float:
        return self._decay_riskiness

    def get_increase_attentiveness_factor(self) -> float:
        return self._increase_attentiveness

    def get_increase_riskiness_factor(self) -> float:
        return self._increase_riskiness

    def get_agents(self) -> float:
        return self._agents

    def get_n_agents(self) -> float:
        return self._n_agents

    def step(self) -> None:
        """
        Method that steps every agent.
        """
        self.schedule_Police.step()
        self.schedule_Thief.step()
        self.schedule_Target.step()
        self.schedule.step()
        self.schedule.steps += 1
        self.schedule.time += 1
        self.datacollector.collect(self)


if __name__ == "__main__":
    model = BaseModel()
