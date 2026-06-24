import mesa
from person import Person
from police import Police

import numpy as np
import random


class Victim(Person):
    def __init__(
        self, unique_id: int, model, pos: tuple[int, int], vision_radius: int
    ) -> None:
        super().__init__(unique_id, model, pos, vision_radius)
        self.wealth = np.random.uniform()
        self.attentiveness = np.random.uniform() 
        #TODO initial attentiveness aligns with wealth?
        self.robbed_timestamp = 0
        self.recovery_time_threshold = 50
        self.recovery_time_remaining = 0
        self._recovered_state = True

    def step(self):
        if self._recovered_state:
            self.move()
        else:
            self.move_to_police()
            self.recovery_time_remaining -= 1
            if self.recovery_time_remaining == 0:
                self._recovered_state = True

        if (
            self.model.schedule.time - self.robbed_timestamp > 5
            and random.random() < 0.01*(1-self.wealth)  # decay probability dependent of wealth
        ):
            # potential victim gets less attentive after not being robbed for some time
            self.attentiveness = max(0, self.attentiveness - self.model.delta)

    def move_to_police(self):
        return self.move_to_type(Police)

    def get_wealth(self):
        return self.wealth

    def get_attentiveness(self):
        return self.attentiveness

    def was_robbed(self):
        self.attentiveness = min(1.0, self.attentiveness + self.model.alpha)
        self.robbed_timestamp = self.model.schedule.time
        self.recovery_time_remaining = self.recovery_time_threshold
        self._recovered_state = False
