import mesa
import base_model
import random


class Person(mesa.Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        self.model = model
        self.pos = pos

    def move(self):
        # Get neighbours (Moore neighbourhood) and randomly select one
        neighbours = self.model.grid.get_neighborhood(self.pos, True)
        selected_neighbour = random.choice(neighbours)
        # Move agent
        self.model.grid.move_agent(self, selected_neighbour)

    def biased_move(self):
        neighbours = self.model.grid.get_neighborhood(self.pos, True)

        # Type of agent
        agent_type = self.__class__.__name__

        if agent_type == "Thief":
            nieghbours_with_passerby = []

            for neighbour in neighbours:
                contents = self.model.grid.get_cell_list_contents([neighbour])

                for content in contents:
                    if content.__class__.__name__ == "Victim":
                        nieghbours_with_passerby.append(neighbour)
                

            if len(nieghbours_with_passerby) > 0:
                selected_neighbour = random.choice(nieghbours_with_passerby)
            
            else:
                selected_neighbour = random.choice(neighbours)

        else:
            selected_neighbour = random.choice(neighbours)

        self.model.grid.move_agent(self, selected_neighbour)

if __name__ == "__main__":
    # Test the Person class with a single agent at (5,5)
    model = base_model.BaseModel()
    model.add_agent(Person, (5, 5))
    person = model.agents[0]
    print(person.pos)
    person.move()
    print(person.pos)