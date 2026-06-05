import mesa
import mesa.space


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


if __name__ == "__main__":
    model = BaseModel()
