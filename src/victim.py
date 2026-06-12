import mesa
from person import Person
# from base_model import BaseModel
import numpy as np
import random


class Victim(Person):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.attentiveness = np.random.uniform()
        self.wealth = np.random.normal()
        self.robbed_timestamp = 0
    
    def step(self):
        self.move()
        if self.model.schedule.time - self.robbed_timestamp > 50:
            # potential victim gets less attentive after not being robbed for some time
            self.attentiveness = max(0, self.attentiveness-0.005)


if __name__ == "__main__":
    model = BaseModel()
    victim = Victim(1, model)
