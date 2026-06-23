import mesa
import mesa.space
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import victim
import police
import thief
from heatmap import HeatmapTile
import numpy as np
import random


class BaseModel(mesa.Model):
    def __init__(
        self, width=50, height=50, police_vision_radius=8, thief_vision_radius=3
    ):
        super().__init__()

        self.height = height
        self.width = width
        self.n_thieves = 10
        self.n_victims = 1500
        self.n_police = 5

        self.police_vision_radius = police_vision_radius
        self.thief_vision_radius = thief_vision_radius
        self.victim_vision_radius = 1

        self.schedule_Police = RandomActivation(self)
        self.schedule_Victim = RandomActivation(self)
        self.schedule_Thief = RandomActivation(self)

        self.schedule = RandomActivation(self)

        self.grid = mesa.space.MultiGrid(width, height, False)

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
                    if isinstance(agent, victim.Victim)
                )
                / self.n_victims,
                "Avg Riskyness": lambda m: sum(
                    agent.riskyness
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
        self.init_population_police_patrol(self.n_police)
        self.init_population(thief.Thief, self.n_thieves)
        self.init_population(victim.Victim, self.n_victims)

        self.running = True
        self.datacollector.collect(self)

    def add_agent(self, agent_type: type, pos):
        match agent_type:
            case police.Police:
                vision_radius = self.police_vision_radius
            case victim.Victim:
                vision_radius = self.victim_vision_radius
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

    def remove_agent(self, agent):
        # Remove from the grid
        self.grid.remove_agent(agent)

        # Remove agent from the model
        self.agents.remove(agent)

        self.schedule.remove(agent)

        getattr(self, f"schedule_{type(agent).__name__}").remove(agent)

        # Update household values
        self.n_agents = len(self.agents)

    def init_population(self, agent_type, n):
        for _ in range(n):
            i = random.randint(0, self.grid.width - 1)
            j = random.randint(0, self.grid.height - 1)
            if (i, j) in self.grid.empties:
                self.add_agent(agent_type, (i, j))

    def init_population_police_patrol(self, n):
        # Initial population when there is a fixed patrol route for police
        j = [random.randint(0, self.grid.height - 1) for _ in range(n)]
        i = np.linspace(5, self.grid.width - 6, n, dtype=int)
        for k in range(n):
            self.add_agent(police.Police, (int(i[k]), int(j[k])))

    def get_local_business(self, pos: tuple[int, int]) -> float:
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

    def step(self):
        """
        Method that steps every agent.
        """
        self.schedule_Police.step()
        self.schedule_Thief.step()
        self.schedule_Victim.step()
        self.schedule.step()
        self.schedule.steps += 1
        self.schedule.time += 1
        self.datacollector.collect(self)

    def run_model(self, step_count=200):
        for i in range(step_count):
            self.step()


if __name__ == "__main__":
    model = BaseModel()
