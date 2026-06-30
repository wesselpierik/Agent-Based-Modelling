import random
import numpy as np
from person import Person
from target import Target
from police import Police
from heatmap import HeatmapTile


class Thief(Person):
    def __init__(
        self, unique_id: int, model, pos: tuple[int, int], vision_radius: int
    ) -> None:
        """
        Initializes a Thief agent

        Args:
            unique_id:     A unique identifier for the agent.
            model:         The  Mesa simulation model.
            pos:           Initial (x, y) coordinates on the grid.
            vision_radius: Maximum grid distance the thief can see police.
        """
        super().__init__(unique_id, model, pos, vision_radius)
        self._riskiness = np.random.uniform()
        self.succesful_steals = 0
        self.attempts = 0

        self.loot = model.get_loot()
        self.fine = model.get_fine()

    def step(self) -> None:
        """
        Executes the Thief's behavior turn during a model step.
          1. Move toward most crowded zone.
          2. Evaluate surrounding targets sorted by high wealth
             and low attentiveness.
          3. Scan the vision radius for police presence.
          4. Calculate game-theoretic utility for a theft attempt;
             execute if utility > 0.
          5. Dynamically increase riskiness if no attempt is made.
        """
        self.move_to_crowd()

        neighbors_in_vision = self.model.grid.get_neighbors(
            self.pos, moore=True
        )
        targets = [
            obj for obj in neighbors_in_vision if isinstance(obj, Target)
        ]
        if targets:
            # sort targets based on how attractive they are
            targets.sort(key=lambda v: -v.get_attentiveness() + v.get_wealth())
        else:
            return

        # Search for police in vision radius
        neighbors_in_vision = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=int(self.get_vision_radius())
        )
        police_in_vision = [
            obj for obj in neighbors_in_vision if isinstance(obj, Police)
        ]
        if police_in_vision:
            pol_att_utility_func = police_in_vision[0].get_attentiveness()
        else:
            pol_att_utility_func = 0

        for target in targets:
            loot = self.loot
            fine = self.fine
            target_att = target.get_attentiveness()
            # calculation based on game theory
            utility_thief = self._riskiness * loot * (1 - target_att) * (
                1 - pol_att_utility_func
            ) - fine * (target_att + pol_att_utility_func)

            if utility_thief > 0:
                self.rob(target, target_att)
                break

            increase_riskiness_factor = (
                1 + self.model.get_increase_riskiness_factor()
            )

            # no attempt made
            self._riskiness = min(
                1, self._riskiness * increase_riskiness_factor
            )

    def rob(
        self,
        other: Person,
        target_attentiveness: float,
    ) -> None:
        """
        Executes a robbery attempt against a chosen target.
        The success probability dependent on both target and
        police attentiveness.
        Failing a robbery decreases thief riskiness. Successfully executing
        a robbery alerts the target, increases thief confidence,
        and logs a heatmap point.

        Args:
            other:                The Target agent that is being robbed.
            target_attentiveness: The target's current awareness score.
        """
        police_vision = self.model.get_police_vision_radius()
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=int(police_vision)
        )
        police = [obj for obj in neighbors if type(obj) is Police]
        police_attentiveness = police[0].get_attentiveness() if police else 0

        self.attempts += 1
        succes = True
        if random.random() < target_attentiveness:
            self.riskiness = max(0, self._riskiness * 0.5)
            succes = False
        if random.random() < police_attentiveness:
            self.riskiness = max(0, self._riskiness * 0.5)
            succes = False

        # succesful pickpocketing event
        if not succes:
            return

        self.succesful_steals += 1
        other.was_robbed()

        # thief gets riskier after success
        self.riskiness = min(1, self._riskiness + 0.05)

        # Update or create heatmap tile
        x, y = self.pos
        self.model.crime_heatmap[x][y] += 1
        cell_contents = self.model.grid.get_cell_list_contents([(x, y)])
        tile_exists = any(
            type(agent) is HeatmapTile for agent in cell_contents
        )

        if not tile_exists:
            new_tile = HeatmapTile(f"tile_{x}_{y}", self.model, (x, y))
            self.model.grid.place_agent(new_tile, (x, y))
            self.model.schedule.add(new_tile)

    def get_riskiness(self) -> float:
        return self._riskiness
