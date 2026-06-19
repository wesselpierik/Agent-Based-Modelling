import mesa
from person import Person

import numpy as np
import random


class Victim(Person):
    def __init__(
        self, unique_id: int, model, pos: tuple[int, int], vision_radius: int
    ) -> None:
        super().__init__(unique_id, model, pos, vision_radius)
        self.attentiveness = np.random.uniform()
        self.wealth = np.random.uniform()
        self.robbed_timestamp = 0

    def step(self):
        self.move()
        if (
            self.model.schedule.time - self.robbed_timestamp > 5
            and random.random() < 0.01*(1-self.wealth)  # decay probability dependent of wealth
        ):
            # potential victim gets less attentive after not being robbed for some time
            self.attentiveness = max(0, self.attentiveness - 0.05)

    def get_wealth(self):
        return self.wealth

    def get_attentiveness(self):
        return self.attentiveness

    def was_robbed(self):
        self.attentiveness = max(1.0, self.attentiveness + 0.5)
        self.robbed_timestamp = self.model.schedule.time
