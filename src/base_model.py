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
        width=50,
        height=50,
        police_vision_radius=8,
        thief_vision_radius=3,
        police_attentiveness=1,
        risk=1,
        n_police=5,
        decay_attentiveness=0.1,
        increase_attentiveness=0.5,
        increase_riskiness=0.05,
        loot=5,
        fine=2,
        **kwargs,
    ) -> None:
        """
        Initializes the model

        Args:
            width (int): width of the grid
            height (int): height of the grid
            police_vision_radius (int): radius of cells police can see
            thief_vision_radius (int): radius of cells a thief can see
            police_attentiveness (float): attentiveness of police agents
            risk (float): global environmental risk multiplier
            n_police (int): amount of police agents
        """
        super().__init__()
        # set all parameters
        self.height = height
        self.width = width
        self.n_thieves = 5
        self.n_victims = 1500
        self.n_police = n_police

        self.police_vision_radius = police_vision_radius
        self.thief_vision_radius = thief_vision_radius
        self.target_vision_radius = 1

        self.loot = loot
        self.fine = fine

        self.schedule_Police = RandomActivation(self)
        self.schedule_Target = RandomActivation(self)
        self.schedule_Thief = RandomActivation(self)

        self.schedule = RandomActivation(self)

        self.grid = mesa.space.MultiGrid(width, height, False)

        # Collect data for plots in server.py
        self.datacollector = DataCollector(
            {
                "Attempts": lambda m: sum(
                    agent.attempts
                    for agent in m.agents
                    if isinstance(agent, thief.Thief)
                ),
                "Succesful": lambda m: (
                    sum(
                        agent.succesful_steals
                        for agent in m.agents
                        if isinstance(agent, thief.Thief)
                    )
                ),
                "Avg Attentiveness": lambda m: sum(
                    agent.attentiveness
                    for agent in m.agents
                    if isinstance(agent, target.Target)
                )
                / self.n_targets,
                "Avg Riskiness": lambda m: sum(
                    agent.riskiness
                    for agent in m.agents
                    if isinstance(agent, thief.Thief)
                )
                / self.n_thieves,
            }
        )

        self.n_agents = 0
        self.agents = []
        self.crime_heatmap = np.zeros((width, height))

        # Create initial population of agents
        self.init_population_police_patrol(
            self.n_police
        )  # Change to self.init_population_police_patrol(self.n_police) for patrol movement
        self.init_population(thief.Thief, self.n_thieves)
        self.init_population(target.Target, self.n_targets)

        self.running = True
        self.datacollector.collect(self)

    def add_agent(self, agent_type: type, pos) -> None:
        """
        Instantiates a specific type of agent

        Args:
            agent_type (type): Class of agent (Police, Thief, Target).
            pos (tuple[int, int]): Coordinate pair (x, y) target placement.
        
        Raises ValueError if an unexpected class object is passed.
        """
        match agent_type:
            case police.Police:
                vision_radius = self.police_vision_radius
            case target.Target:
                vision_radius = self.target_vision_radius
            case thief.Thief:
                vision_radius = self.thief_vision_radius
            case _:
                raise ValueError(
                    f"Trying to add an unknown class of agent type {agent_type}"
                )

        # Create new agent
        new_agent = agent_type(self.n_agents, self, pos, vision_radius)

        # Place the agent in the grid
        self.grid.place_agent(new_agent, pos)

        # Add the agent to the model
        self.agents.append(new_agent)

        # Update the household value
        self.n_agents = len(self.agents)

        self.schedule.add(new_agent)
        getattr(self, f"schedule_{agent_type.__name__}").add(new_agent)

    def remove_agent(self, agent) -> None:
        """
        Removes agent from the grid, model and schedule
        """
        self.grid.remove_agent(agent)
        self.agents.remove(agent)
        self.schedule.remove(agent)
        getattr(self, f"schedule_{type(agent).__name__}").remove(agent)

        # Update household values
        self.n_agents = len(self.agents)

    def init_population(self, agent_type, n: int) -> None:
        """
        Adds the desired amount of agents to the grid

        Args:
            agent_type (type): Class of agent to add.
            n (int): Amount of agents to add.
        """
        agents_spawned = 0
        while agents_spawned < n:
            i = random.randint(0, self.grid.width - 1)
            j = random.randint(0, self.grid.height - 1)

            if (i, j) in self.grid.empties:
                self.add_agent(agent_type, (i, j))
                agents_spawned += 1  # Only count successful spawns!


    def init_population_police_patrol(self, n: int):
        """
        Adds the desired amount of police to the grid with a certain 
        amount of horizontal space between them

        Args:
            n (int): Amount of patrolling police officers to add.
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
        neighborhood of radius 10.

        Args:
            pos (tuple[int, int]): cell location of the checking agent.

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
        return self.police_attentiveness

    def get_successful_thefts(self) -> int:
        return self.datacollector.get_model_vars_dataframe()["Succesful"]

    def get_caught_thieves(self) -> int:
        return (
            self.datacollector.get_model_vars_dataframe()["Attempts"]
            - self.datacollector.get_model_vars_dataframe()["Succesful"]
        )

    def get_loot(self):
        return self.loot

    def get_fine(self):
        return self.fine

    def step(self):
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

    def run_model(self, step_count=200) -> None:
        """
        I believe we use this never
        """
        for i in range(step_count):
            self.step()


if __name__ == "__main__":
    model = BaseModel()
