import mesa
import random
from person import Person
# from base_model import BaseModel
from victim import Victim
from police import Police


class Thief(Person):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.riskyness = random.uniform(0,1)
        self.succesful_steals = 0

    def step(self):
        self.move()
        
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True)
        potential_victims = [obj for obj in neighbors if isinstance(obj, Victim)]
        if potential_victims:
            best_victim = max(potential_victims, key=lambda v: (1 - v.attentiveness) + v.wealth)
            if best_victim.attentiveness > 0.9:
                return # no good options, move on
        
        # Search for police in randius 3
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, radius=3)
        police_nearby = [obj for obj in neighbors if isinstance(obj, Police)]
        if police_nearby:
            police_parameter = 1 / (1+len(police_nearby)) # gets smaller with more police

        grid_size = self.model.grid.width * self.model.grid.height
        amount_of_people = self.model.n_agents # Total agents in simulation
        busyness_parameter = amount_of_people / grid_size # as it gets busier, gets closer to 1 

        prob_caught = ((1-police_parameter)+(1-busyness_parameter))/2
        if self.riskyness > prob_caught:
            if random.random() < prob_caught:
                # TODO implement jailtime ?
                self.riskyness = max(0, self.riskyness-0.1)
            else:
                self.succesful_steals += 1
                best_victim.attentiveness = min(1.0, best_victim.attentiveness + 0.1)
                # TODO: wealth of victim changes??


if __name__ == "__main__":
    model = BaseModel()
    thief = Thief(1, model)