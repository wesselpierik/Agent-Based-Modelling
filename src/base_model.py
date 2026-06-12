import mesa
import mesa.space
from victim import Victim
from police import Police
from thief import Thief
import random

class BaseModel(mesa.Model):
    def __init__(self, width=100, height=100):
        super().__init__()

        self.height = height
        self.width = width
        self.n_thieves = 5
        self.n_victims = 100
        self.n_police = 5

        self.grid = mesa.space.MultiGrid(width, height, True)

        self.n_agents = 0
        self.agents = []

        # Create initial population of agents
        self.init_population(Thief, self.n_thieves)
        self.init_population(Police, self.n_police)
        self.init_population(Victim, self.n_victims)

    def add_agent(self, agent_type, pos):
        # Create new agent
        new_agent = agent_type(self.n_agents, self, pos)

        # Place the agent in the grid
        self.grid.place_agent(new_agent, pos)

        # Add the agent to the model
        self.agents.add(new_agent)

        # Update the household value
        self.n_agents = len(self.agents)

    def remove_agent(self, agent):
        # Remove from the grid
        self.grid.remove_agent(agent)

        # Remove agent from the model
        self.agents.remove(agent)

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
        for agent in list(self.agents):
            agent.step()

if __name__ == "__main__":
    model = BaseModel()
    # positions = []
    # for _ in range(12):
    #     i = random.randint(0, 10)
    #     j = random.randint(0, 10)
    #     if (i,j) not in positions:
    #         positions.append((i,j)) 
    # for i in range(len(positions)-2):
    #     model.add_agent(Victim, positions[i])
    # model.add_agent(Police, positions[10])
    # model.add_agent(Thief, positions[-1])
    iterations = 50
    for _ in range(iterations):
        model.step()


