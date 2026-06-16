import mesa
import math
import numpy as np
# import base_model
import random

class Person(mesa.Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        # self.model = model
        self.pos = pos

    def move(self):
        # Get neighbours (Moore neighbourhood) and randomly select one that is empty
        neighbours = self.model.grid.get_neighborhood(self.pos, True)

        # Check for empty neighbours
        empty_neighbours = []
        for neighbour in neighbours:
            contents = self.model.grid.get_cell_list_contents([neighbour])
            filter_tiles = [agent for agent in contents if not isinstance(agent, HeatmapTile)]
        
            # If there are no physical people in the cell, it's safe to move there!
            if len(filter_tiles) == 0:
                empty_neighbours.append(neighbour)

        if len(empty_neighbours) != 0:
            selected_neighbour = random.choice(empty_neighbours)

        else:
            # No movement if there are no empty neighbours
            return
        
        # Move agent
        self.model.grid.move_agent(self, selected_neighbour)

    def biased_move(self):
        # Get neighbours (Moore neighbourhood)
        neighbours = self.model.grid.get_neighborhood(self.pos, True)

        # Check for empty neighbours
        empty_neighbours = []
        for neighbour in neighbours:
            contents = self.model.grid.get_cell_list_contents([neighbour])
            
            filter_tiles = [agent for agent in contents if not isinstance(agent, HeatmapTile)]
            if len(filter_tiles) == 0:
                empty_neighbours.append(neighbour)

        if len(empty_neighbours) == 0:
            # No movement if there are no empty neighbours
            return
        
        else:
            # Type of agent
            agent_type = self.__class__.__name__

            # Biased moevement for thieves
            # Move to neighbour with most potential victims as neighbours (Moore neighbourhood)
            if agent_type == "Thief":
                n_passerby_neighbour = []
                for neighbour in empty_neighbours:
                    contents = self.model.grid.get_cell_list_contents([neighbour])
                    
                    filter_tiles = [agent for agent in contents if not isinstance(agent, HeatmapTile)]
                    if len(filter_tiles) == 0:
                        neighbours_of_neighbour = self.model.grid.get_neighborhood(neighbour, True)
                        passerby_count = 0

                        # For each neighbour of the neighbour, count the number of potential victims
                        for n in neighbours_of_neighbour:
                            contents = self.model.grid.get_cell_list_contents([n])
                            filter_tiles = [agent for agent in contents if not isinstance(agent, HeatmapTile)]
                            
                            for content in filter_tiles:
                                if content.__class__.__name__ == "Victim":
                                    passerby_count += 1

                        n_passerby_neighbour.append((neighbour, passerby_count))

                    else:
                        # Skip neighhbour if it is not empty
                        continue

                # Select neighbour with most potential victims
                if len(n_passerby_neighbour) > 0:
                    values = [x[1] for x in n_passerby_neighbour]
                    max_value = max(values)

                    max_indices = []
                    for index, value in enumerate(values):
                        if value == max_value:
                            max_indices.append(index)

                    selected_neighbour = n_passerby_neighbour[random.choice(max_indices)][0]

            else:
                selected_neighbour = random.choice(empty_neighbours)

            self.model.grid.move_agent(self, selected_neighbour)
    
    
    def move_to_crowd(self):
        # Biased movement of agents towards the bussiest spot within their range

        # Get neighbours (Moore neighbourhood)
        neighbours = self.model.grid.get_neighborhood(self.pos, True)

        # Check for empty neighbours
        empty_neighbours = []
        for neighbour in neighbours:
            contents = self.model.grid.get_cell_list_contents([neighbour])
            
            filter_tiles = [agent for agent in contents if not isinstance(agent, HeatmapTile)]
            if len(filter_tiles) == 0:
                empty_neighbours.append(neighbour)

        if len(empty_neighbours) == 0:
            # No movement if there are no empty neighbours
            return
        
        else:
            # Move to crowd
            radius = self.model.grid.get_neighborhood(self.pos, True, radius=8)
            contents =  self.model.grid.get_cell_list_contents(radius)
            coords = []
            for agent in contents:
                coords.append(agent.pos)
            m = tuple(map(float, np.mean(coords, axis=0)))
            # nb = self.model.grid.get_neighborhood(pos=self.pos, moore=True)
            new_pos = min(empty_neighbours, key=lambda c: math.dist(c, m))
            self.model.grid.move_agent(self, new_pos)

        pass

    def move_to_police(self):
        # Biased movement where agent wants to move towards police presence
        police_locations = []

        for agent in self.model.agents:
            if agent.__class__.__name__ == "Police":
                police_locations.append(agent.pos)
        
        # Get closest police location
        closest_police = None
        min_distance = float('inf')

        if len(police_locations) > 0:
            for loc in police_locations:
                distance = math.dist(self.pos, loc)
                if distance < min_distance:
                    min_distance = distance
                    closest_police = loc

    def apparent_wealth(self):
        # Biased movement of agents when there is apparent wealth in the model
        pass

    def perceived_police(self):
        # Biased movement of thieves when there is perceived police presence in the model
        pass

    def get_wealth(self):
        raise NotImplementedError
    
    def get_attentiveness(self):
        raise NotImplementedError
    
    def was_robbed(self):
        raise NotImplementedError
    
    def get_local_business(self) -> float:
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
        return amount_of_people_local / local_grid_size

class HeatmapTile(Person):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        
    def step(self):
        pass

    
if __name__ == "__main__":
    # Test the Person class with a single agent at (5,5)
    model = base_model.BaseModel()
    # model.add_agent(Person, (5, 5))
    # person = model.agents[0]
    # print(person.pos)
    # person.move()
    # print(person.pos)