import mesa
import random
from person import Person, HeatmapTile
# from base_model import BaseModel
from victim import Victim
from police import Police


class Thief(Person):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.riskyness = random.uniform(0,1)
        self.succesful_steals = 0
        self.attempts = 0

    def step(self):
        self.biased_move()
        
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True)
        potential_victims = [obj for obj in neighbors if isinstance(obj, Victim)]
        if potential_victims:
            best_victim = max(potential_victims, key=lambda v: -v.attentiveness + v.wealth)
            if best_victim.attentiveness > 0.9:
                return # no good options, move on
        else:
            return
        
        # Search for police in randius 3
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, radius=round(self.model.width/5))
        police_nearby = [obj for obj in neighbors if isinstance(obj, Police)]

        # local busyness
        local_cells = self.model.grid.get_neighborhood(
            self.pos, 
            moore=True, 
            include_center=True, 
            radius=10
        )
        local_contents = self.model.grid.get_cell_list_contents(local_cells)
        local_people = [agent for agent in local_contents if not isinstance(agent, HeatmapTile)]
        amount_of_people_local = len(local_people)
        local_grid_size = len(local_cells)
        busyness_parameter = amount_of_people_local / local_grid_size

        if police_nearby:
            police_parameter=0.8 
        else:
            police_parameter=0

        prob_caught = (0.8*police_parameter+0.2*(1-busyness_parameter))/2
        if self.riskyness > prob_caught:
            self.attempts += 1
            if random.random() < prob_caught:
                self.riskyness = max(0, self.riskyness-0.1)
            else:
                # succesful pickpocketing event
                self.succesful_steals += 1
                best_victim.attentiveness = max(1.0, best_victim.attentiveness + 0.5)
                best_victim.robbed_timestamp = self.model.schedule.time 
                self.riskyness = min(1, self.riskyness +0.05)
                x, y = self.pos
                self.model.crime_heatmap[x][y] += 1
                cell_contents = self.model.grid.get_cell_list_contents([(x, y)])
                tile_exists = any(isinstance(agent, HeatmapTile) for agent in cell_contents)
                
                # Only spawn a tile if this is the first crime in this cell!
                if not tile_exists:
                    new_tile = HeatmapTile(f"tile_{x}_{y}", self.model, (x, y))
                    self.model.grid.place_agent(new_tile, (x, y))
                    self.model.schedule.add(new_tile)

    def move_to_wealth(self):
        return super().move_to_wealth()  

if __name__ == "__main__":
    model = BaseModel()
    thief = Thief(1, model)