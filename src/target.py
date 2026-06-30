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
        Initializes a Target agent with randomized wealth and
        awareness baselines.

        Args:
            unique_id:     A unique identifier for the agent instance.
            model:         The simulation model.
            pos:           Initial (x, y) coordinates on the grid map.
            vision_radius: Vision threshold.
        """
        super().__init__(unique_id, model, pos, vision_radius)
        self._wealth = np.random.uniform()
        self._attentiveness = np.random.uniform()
        self._robbed_timestamp = 0
        self._recovery_time_threshold = 50
        self._recovery_time_remaining = 0
        self._recovered_state = True

    def step(self) -> None:
        """
        Executes the Target's behavioral loop during a single model step.
        Moves randomly along adjacent spaces unless just after being robbed,
        then it moves toward nearby police agents.

        If unbothered for 5 steps, awareness score degrades based on a
        probability inversely proportional to their wealth value.
        """
        if self._recovered_state:
            self.move()
        else:
            self.move_to_police()
            self._recovery_time_remaining -= 1
            if self._recovery_time_remaining == 0:
                self._recovered_state = True

        if (
            self.model.schedule.time - self._robbed_timestamp > 5
            and random.random()
            < 0.01
            * (1 - self._wealth)  # decay probability dependent of wealth
        ):
            # targets gets less attentive after not being robbed for some time
            self._attentiveness = max(
                0,
                self._attentiveness
                - self.model.get_decay_attentiveness_factor(),
            )

    def move_to_police(self) -> None:
        """
        A wrapper to the move_to_type function specifically for the police
        """
        return self.move_to_type(Police)

    def get_wealth(self) -> float:
        return self._wealth

    def get_attentiveness(self) -> float:
        return self._attentiveness

    def was_robbed(self) -> None:
        """
        Event callback executed upon a successful pickpocketing attack.

        Increases attentiveness level, saves the time when she was robbed
        triggers the non-recovered state flag, and initializes the
        police-seeking routing timer.
        """
        attentiveness_increase = self.model.get_increase_attentiveness_factor()

        self._attentiveness = min(
            1.0, self._attentiveness + attentiveness_increase
        )
        self._robbed_timestamp = self.model.schedule.time
        self._recovery_time_remaining = self._recovery_time_threshold
        self._recovered_state = False

    def neighbor_was_robbed(self) -> None:
        """
        Event callback executed if an adjacent peer within witnessing
        distance gets robbed.

        Not used in the actual simulation runs.
        """
        # Neighbors get more alert, but less than the actual victim
        witness_shock = 0.15

        # Increase their attentiveness and update their timestamp
        # so they don't instantly decay
        self._attentiveness = min(1.0, self._attentiveness + witness_shock)
        self._robbed_timestamp = self.model.schedule.time
