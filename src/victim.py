import mesa
from person import Person
from base_model import BaseModel
import numpy as np
import random


class Victim(Person):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.attentiveness = np.random.uniform()
        self.wealth = np.random.normal()
    
    def step(self):
        self.move()


if __name__ == "__main__":
    model = BaseModel()
    victim = Victim(1, model)
