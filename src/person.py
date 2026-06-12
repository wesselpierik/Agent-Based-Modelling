import mesa
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
            if len(contents) == 0:
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
            if len(contents) == 0:
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
                    
                    if len(contents) == 0:
                        neighbours_of_neighbour = self.model.grid.get_neighborhood(neighbour, True)
                        passerby_count = 0

                        # For each neighbour of the neighbour, count the number of potential victims
                        for n in neighbours_of_neighbour:
                            contents = self.model.grid.get_cell_list_contents([n])

                            for content in contents:
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

    def apparent_wealth(self):
        # Biased movement of agents when there is apparent wealth in the model
        pass

    def perceived_police(self):
        # Biased movement of thieves when there is perceived police presence in the model
        pass

if __name__ == "__main__":
    # Test the Person class with a single agent at (5,5)
    model = base_model.BaseModel()
    # model.add_agent(Person, (5, 5))
    # person = model.agents[0]
    # print(person.pos)
    # person.move()
    # print(person.pos)