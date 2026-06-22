import mesa
import random
import numpy as np
from person import Person
from victim import Victim
from police import Police
from heatmap import HeatmapTile


class Thief(Person):
    def __init__(self, unique_id: int, model, pos: tuple[int, int], vision_radius: int) -> None:
        super().__init__(unique_id, model, pos, vision_radius)
        self.riskyness = np.random.uniform()
        self.succesful_steals = 0
        self.attempts = 0

    def step(self):
        self.move_to_wealth()
        
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True)
        potential_victims = [obj for obj in neighbors if isinstance(obj, Victim)]
        if potential_victims:
            best_victim = max(
                potential_victims, key=lambda v: -v.get_attentiveness() + v.get_wealth()
            )
            if best_victim.get_attentiveness() > 0.9:
                return  # no good options, move on
        else:
            return

        # Search for police in vision radius
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=self.model.thief_vision_radius
        )
        police_nearby = [obj for obj in neighbors if isinstance(obj, Police)]

        # local busyness
        business_parameter = self.get_local_business()

        if police_nearby:
            police_parameter = 0.8
        else:
            police_parameter = 0

        prob_caught = (
            0.5 * police_parameter
            + 0.2 * (1 - business_parameter)
            + 0.3 * (1 - best_victim.get_attentiveness())
        )
        if self.riskyness > prob_caught:
            self.rob(best_victim, prob_caught)

    def rob(self, other: Person, prob_caught: float):
        self.attempts += 1
        if random.random() < prob_caught:
            self.riskyness = max(0, self.riskyness - 0.09)
            return

        # succesful pickpocketing event
        self.succesful_steals += 1
        other.was_robbed()
        self.riskyness = min(1, self.riskyness + 0.05) # update riskyness

        # Update or create heatmap tile
        x, y = self.pos
        self.model.crime_heatmap[x][y] += 1
        cell_contents = self.model.grid.get_cell_list_contents([(x, y)])
        tile_exists = any(isinstance(agent, HeatmapTile) for agent in cell_contents)

        if not tile_exists:
            new_tile = HeatmapTile(f"tile_{x}_{y}", self.model, (x, y))
            self.model.grid.place_agent(new_tile, (x, y))
            self.model.schedule.add(new_tile)

    def move_to_wealth(self):
        return super().move_to_wealth()
