import mesa
import random
import numpy as np
from person import Person
from victim import Victim
from police import Police
from heatmap import HeatmapTile


class Thief(Person):
    def __init__(
        self, unique_id: int, model, pos: tuple[int, int], vision_radius: int
    ) -> None:
        super().__init__(unique_id, model, pos, vision_radius)
        self.riskiness = np.random.uniform()
        self.succesful_steals = 0
        self.attempts = 0

        self.loot = model.get_loot()
        self.fine = model.get_fine()

    def step(self):
        self.move_to_crowd()

        neighbors_in_vision = self.model.grid.get_neighbors(self.pos, moore=True)
        potential_victims = [obj for obj in neighbors_in_vision if isinstance(obj, Victim)]
        if potential_victims:
            # sort victims based on how attractive they are
            potential_victims.sort(
                key=lambda v: -v.get_attentiveness() + v.get_wealth()
            )
        else:
            return

        # Search for police in vision radius
        neighbors_in_vision = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=int(self.vision_radius)
        )
        police_in_vision = [obj for obj in neighbors_in_vision if isinstance(obj, Police)]
        if police_in_vision:
            pol_att_utility_func = police_in_vision[0].get_attentiveness()
        else:
            pol_att_utility_func = 0

        # local business
        business_parameter = self.get_local_business()

        for victim in potential_victims:
            loot = self.loot
            fine = self.fine
            vic_att = victim.get_attentiveness()
            # calculation based on game theory
            utility_thief = self.riskiness * loot * (1 - vic_att) * (
                1 - pol_att_utility_func
            ) - fine * (vic_att + pol_att_utility_func)

            if utility_thief > 0:
                self.rob(victim, vic_att, business_parameter)
                break

            # no attempt made
            self.riskiness = min(1, self.riskiness * 1.1)

    def rob(
        self,
        other: Person,
        victim_attentiveness: float,
        business_parameter: float,
    ):
        police_vision = self.model.police_vision_radius
        neighbors = self.model.grid.get_neighbours(
            self.pos, moore=True, radius=int(police_vision)
        )
        police = [obj for obj in neighbors if isinstance(obj, Police)]
        police_attentiveness = police[0].get_attentiveness() if police else 0

        self.attempts += 1
        succes = True
        if random.random() < victim_attentiveness:
            self.riskiness = max(0, self.riskiness * 0.5)
            succes = False
        if random.random() < police_attentiveness:
            self.riskiness = max(0, self.riskiness * 0.5)
            succes = False

        # succesful pickpocketing event
        if not succes:
            return

        self.succesful_steals += 1
        other.was_robbed()
        self.riskiness = min(1, self.riskiness + self.model.beta)

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
