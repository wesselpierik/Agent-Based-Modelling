import mesa
from person import Person
from police import Police

import numpy as np
import random


class Target(Person):
    """
    An agent representing a target (potential victim).
    Maintains variables for personal wealth and dynamic attentiveness levels.
    Targets get less attentive over time if left undisturbed.
    """
    def __init__(
        self, unique_id: int, model, pos: tuple[int, int], vision_radius: int
    ) -> None:
        """
        Initializes a Target agent with randomized wealth and awareness baselines.

        Args:
            unique_id (int): A unique identifier for the agent instance.
            model (Model): The simulation model.
            pos (tuple[int, int]): Initial (x, y) coordinates on the grid map.
            vision_radius (int): Vision threshold.
        """
        super().__init__(unique_id, model, pos, vision_radius)
        self.wealth = np.random.uniform()
        self.attentiveness = np.random.uniform() 
        #TODO initial attentiveness aligns with wealth?
        self.robbed_timestamp = 0
        self.recovery_time_threshold = 50
        self.recovery_time_remaining = 0
        self._recovered_state = True

    def step(self) -> None:
        """
        Executes the Target's behavioral loop during a single model step.
        Moves randomly along adjacent spaces unless just after being robbed,
        then it moves toward nearby police agents.
            
        If unbothered for 5 steps, awareness score degrades based on a probability 
        inversely proportional to their wealth value.
        """
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
            # targets gets less attentive after not being robbed for some time
            self.attentiveness = max(0, self.attentiveness - 0.1)

    def move_to_police(self) -> None:
        return self.move_to_type(Police)

    def get_wealth(self) -> float:
        return self.wealth

    def get_attentiveness(self) -> float:
        return self.attentiveness

    def was_robbed(self) -> None:
        """
        Event callback executed upon a successful pickpocketing attack.
        
        Increases attentiveness level, saves the time when she was robbed
        triggers the non-recovered state flag, and initializes the police-seeking routing timer.
        """
        self.attentiveness = min(1.0, self.attentiveness + 0.5)
        self.robbed_timestamp = self.model.schedule.time
        self.recovery_time_remaining = self.recovery_time_threshold
        self._recovered_state = False

    def neighbor_was_robbed(self) -> None:
        """
        Event callback executed if an adjacent peer within witnessing distance gets robbed.
        """
        witness_shock = 0.15 # Neighbors get more alert, but less than the actual victim
        # Increase their attentiveness and update their timestamp so they don't instantly decay
        self.attentiveness = min(1.0, self.attentiveness + witness_shock)
        self.robbed_timestamp = self.model.schedule.time 
