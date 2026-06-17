import mesa
import math
# import base_model
import random

class Person(mesa.Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        # self.model = model
        self.pos = pos

    def empty_neighbourhood(self, neighbours):
        # Check for empty neighbours
        empty_neighbours = []
        for neighbour in neighbours:
            contents = self.model.grid.get_cell_list_contents([neighbour])
            filter_tiles = [agent for agent in contents if not isinstance(agent, HeatmapTile)]
        
            if len(filter_tiles) == 0:
                empty_neighbours.append(neighbour)

        return empty_neighbours

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

    def move_to_police(self):
        # Biased movement where agent wants to move towards police presence
        police_locations = []

        for agent in self.model.agents:
            if agent.__class__.__name__ == "Police":
                police_locations.append(agent.pos)
        
        # Get closest police location
        closest_police = None
        min_distance = 9999999

        if len(police_locations) > 0:
            for loc in police_locations:
                distance = math.dist(self.pos, loc)
                if distance < min_distance:
                    min_distance = distance
                    closest_police = loc
        
        # Move towards closest police location
        if closest_police is not None:
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
                # Select neighbour that is closest to police location
                closest_neighbour = None
                min_distance = 9999999

                for neighbour in empty_neighbours:
                    distance = math.dist(neighbour, closest_police)
                    if distance < min_distance:
                        min_distance = distance
                        closest_neighbour = neighbour
                
                self.model.grid.move_agent(self, closest_neighbour)

        else:
            # Move randomly if there is no police
            self.move()

    def apparent_wealth(self):
        return None
    
    def move_to_wealth(self):
        # Agents move towards victims with higher apparent wealth
        # Get neighbours (Moore neighbourhood)
        neighbours = self.model.grid.get_neighborhood(self.pos, True)
        empty_neighbours = self.empty_neighbourhood(neighbours)

        if len(empty_neighbours) == 0:
            # No movement if there are no empty neighbours
            return
                        
        else:
            max_apparent_wealth = []
            for surrounding_cell in empty_neighbours:
                # Get neighbours of surrounding cell
                neighbours_surrounding = self.model.grid.get_neighborhood(surrounding_cell, True)

                # Get apparent wealth of each neighbour
                apparent_wealth = []
                for neighbour in neighbours_surrounding:
                    contents = self.model.grid.get_cell_list_contents([neighbour])
                    filter_tiles = [agent for agent in contents if not isinstance(agent, HeatmapTile)]
                    
                    for content in filter_tiles:
                        if content.__class__.__name__ == "Victim":
                            apparent_wealth.append(content.get_apparent_wealth())

                if len(apparent_wealth) > 0:
                    max_apparent_wealth.append((surrounding_cell, max(apparent_wealth)))

            # Select neighbour with wealthies neighbour
            if len(max_apparent_wealth) > 0:
                values = [x[1] for x in max_apparent_wealth]
                max_value = max(values)

                max_indices = []
                for index, value in enumerate(values):
                    if value == max_value:
                        max_indices.append(index)

                selected_neighbour = max_apparent_wealth[random.choice(max_indices)][0]
                
            else:
                print("something went wrong")
                selected_neighbour = random.choice(empty_neighbours)
            
            self.model.grid.move_agent(self, selected_neighbour)
                
    def perceived_police(self):
        # Biased movement of thieves when there is perceived police presence in the model
        pass

class HeatmapTile(Person):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        
    def step(self):
        x, y = self.pos
        
        # Decrease the crime count by a fraction every timestep (e.g., 0.1)
        # This allows smooth transitioning down through your color brackets
        if self.model.crime_heatmap[x][y] > 0:
            self.model.crime_heatmap[x][y] = max(0, self.model.crime_heatmap[x][y] - 0.1)
            
        # Once the crime count completely cools down to 0, remove the tile
        if self.model.crime_heatmap[x][y] == 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)


if __name__ == "__main__":
    # Test the Person class with a single agent at (5,5)
    model = base_model.BaseModel()
    # model.add_agent(Person, (5, 5))
    # person = model.agents[0]
    # print(person.pos)
    # person.move()
    # print(person.pos)