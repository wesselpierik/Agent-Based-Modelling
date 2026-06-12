import mesa
import mesa.space
from victim import Victim
from police import Police
from thief import Thief
import random



class BaseModel(mesa.Model):
    def __init__(self, width=10, height=10):
        super().__init__()

        self.grid = mesa.space.MultiGrid(width, height, True)

        self.n_agents = 0
        self.agents = []

    def add_agent(self, agent_type, pos):
        # Create new agent
        new_agent = agent_type(self.n_agents, self, pos)

        # Place the agent in the grid
        self.grid.place_agent(new_agent, pos)

        # Add the agent to the model
        self.agents += [new_agent]

        # Update the household value
        self.n_agents = len(self.agents)

    def remove_agent(self, agent):
        # Remove from the grid
        self.grid.remove_agent(agent)

        # Remove agent from the model
        self.agents.remove(agent)

        # Update household values
        self.n_agents = len(self.agents)

    def step(self):
        '''
        Method that steps every agent. 
        '''
        for agent in list(self.agents):
            agent.step()

if __name__ == "__main__":
    model = BaseModel()
    positions = []
    for _ in range(12):
        i = random.randint(0, 10)
        j = random.randint(0, 10)
        if (i,j) not in positions:
            positions.append((i,j)) 
    for i in range(len(positions)-2):
        model.add_agent(Victim, positions[i])
    model.add_agent(Police, positions[10])
    model.add_agent(Thief, positions[-1])
    iterations = 50
    for _ in range(iterations):
        model.step()


