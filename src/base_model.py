import mesa
import mesa.space
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from victim import Victim
from police import Police
from thief import Thief
from person import HeatmapTile
import random
import numpy as np

class BaseModel(mesa.Model):
    def __init__(self, width=50, height=50):
        super().__init__()

        self.height = height
        self.width = width
        self.n_thieves = 50
        self.n_victims = 1000
        self.n_police = 3

        self.schedule_Victim = RandomActivation(self)
        self.schedule_Thief = RandomActivation(self)
        self.schedule_Police = RandomActivation(self)

        self.schedule = RandomActivation(self)

        self.grid = mesa.space.MultiGrid(width, height, False)

        self.datacollector = DataCollector(
             {"Attempts": lambda m: sum(agent.attempts for agent in m.agents if isinstance(agent, Thief)),
              "Succesful": lambda m: (sum(agent.succesful_steals for agent in m.agents if isinstance(agent, Thief))),
              "Avg Attentiveness": lambda m: sum(agent.attentiveness for agent in m.agents if isinstance(agent, Victim))/self.n_victims,
              "Avg Riskyness": lambda m: sum(agent.riskyness for agent in m.agents if isinstance(agent, Thief))/self.n_thieves})

        self.n_agents = 0
        self.agents = []
        self.crime_heatmap = np.zeros((width, height))


        # Create initial population of agents
        self.init_population(Thief, self.n_thieves)
        self.init_population(Police, self.n_police)
        self.init_population(Victim, self.n_victims)

        self.running=True
        self.datacollector.collect(self)

    def add_agent(self, agent_type, pos):
        # Create new agent
        new_agent = agent_type(self.n_agents, self, pos)

        # Place the agent in the grid
        self.grid.place_agent(new_agent, pos)

        # Add the agent to the model
        self.agents.add(new_agent)

        # Update the household value
        self.n_agents = len(self.agents)

        self.schedule.add(new_agent)
        getattr(self, f'schedule_{agent_type.__name__}').add(new_agent)

    def remove_agent(self, agent):
        # Remove from the grid
        self.grid.remove_agent(agent)

        # Remove agent from the model
        self.agents.remove(agent)

        self.schedule.remove(agent)

        getattr(self, f'schedule_{type(agent).__name__}').remove(agent)

        # Update household values
        self.n_agents = len(self.agents)

    def init_population(self, agent_type, n):
        for _ in range(n):
            i = random.randint(0, self.grid.width - 1)
            j = random.randint(0, self.grid.height - 1)
            if (i,j) in self.grid.empties:
                self.add_agent(agent_type, (i, j))

    def step(self):
        '''
        Method that steps every agent. 
        '''
        self.schedule_Police.step()
        self.schedule_Thief.step()
        self.schedule_Victim.step()

        self.schedule.steps += 1
        self.schedule.time += 1
        self.datacollector.collect(self)

    def run_model(self, step_count=200):
        for i in range(step_count):
            self.step()

if __name__ == "__main__":
    model = BaseModel()



