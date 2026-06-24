import mesa
import math
import numpy as np

# import base_model
import random
import heatmap


class Person(mesa.Agent):
    def __init__(self, unique_id: int, model, pos: tuple[int, int], vision_radius: int):
        super().__init__(unique_id, model)

        self.model = model
        self.pos = pos
        self.vision_radius = vision_radius

    def empty_neighbourhood(self, neighbours):
        # Check for empty neighbours
        empty_neighbours = []
        for neighbour in neighbours:
            contents = self.model.grid.get_cell_list_contents([neighbour])
            filter_tiles = [
                agent
                for agent in contents
                if not isinstance(agent, heatmap.HeatmapTile)
            ]

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
            filter_tiles = [
                agent
                for agent in contents
                if not isinstance(agent, heatmap.HeatmapTile)
            ]

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

            filter_tiles = [
                agent
                for agent in contents
                if not isinstance(agent, heatmap.HeatmapTile)
            ]
            if len(filter_tiles) == 0:
                empty_neighbours.append(neighbour)

        if len(empty_neighbours) == 0:
            # No movement if there are no empty neighbours
            return

        else:
            # Type of agent
            agent_type = self.__class__.__name__

            # Biased moevement for thieves
            # Move to neighbour with most targets as neighbours (Moore neighbourhood)
            if agent_type == "Thief":
                n_passerby_neighbour = []
                for neighbour in empty_neighbours:
                    contents = self.model.grid.get_cell_list_contents([neighbour])

                    filter_tiles = [
                        agent
                        for agent in contents
                        if not isinstance(agent, heatmap.HeatmapTile)
                    ]
                    if len(filter_tiles) == 0:
                        neighbours_of_neighbour = self.model.grid.get_neighborhood(
                            neighbour, True
                        )
                        passerby_count = 0

                        # For each neighbour of the neighbour, count the number of targets
                        for n in neighbours_of_neighbour:
                            contents = self.model.grid.get_cell_list_contents([n])
                            filter_tiles = [
                                agent
                                for agent in contents
                                if not isinstance(agent, heatmap.HeatmapTile)
                            ]

                            for content in filter_tiles:
                                if content.__class__.__name__ == "Target":
                                    passerby_count += 1

                        n_passerby_neighbour.append((neighbour, passerby_count))

                    else:
                        # Skip neighhbour if it is not empty
                        continue

                # Select neighbour with most targets
                if len(n_passerby_neighbour) > 0:
                    values = [x[1] for x in n_passerby_neighbour]
                    max_value = max(values)

                    max_indices = []
                    for index, value in enumerate(values):
                        if value == max_value:
                            max_indices.append(index)

                    selected_neighbour = n_passerby_neighbour[
                        random.choice(max_indices)
                    ][0]

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

            filter_tiles = [
                agent
                for agent in contents
                if not isinstance(agent, heatmap.HeatmapTile)
            ]
            if len(filter_tiles) == 0:
                empty_neighbours.append(neighbour)

        if len(empty_neighbours) == 0:
            # No movement if there are no empty neighbours
            return

        # Move to crowd
        radius = self.model.grid.get_neighborhood(self.pos, True, radius=8)
        contents =  self.model.grid.get_cell_list_contents(radius)
        coords = [agent.pos for agent in contents if type(agent).__name__ == "Target"]
        if len(coords) == 0:
            return
        if len(coords) == 1:
            m = coords[0]
        else:
            m = tuple(map(float, np.mean(coords, axis=0)))
        new_pos = min(empty_neighbours, key=lambda c: math.dist(c, m))
        self.model.grid.move_agent(self, new_pos)

    def move_to_type(self, agent_type: type) -> None:
        type_location = [
            agent.pos
            for agent in self.model.agents
            if type(agent) is agent_type
            and math.dist(self.pos, agent.pos) <= self.vision_radius
        ]

        # There are no agents of agent_type in
        if not type_location:
            self.move()
            return

        neighbours = self.model.grid.get_neighborhood(self.pos, True, radius=1)

        empty_neighbours = self.empty_neighbourhood(neighbours)
        if not empty_neighbours:
            self.move()
            return

        average_pos = np.mean(type_location, axis=0)

        closest_neighbor = None
        min_dist = np.inf

        for neighbour in empty_neighbours:
            dist = math.dist(neighbour, average_pos)
            if dist < min_dist:
                min_dist = dist
                closest_neighbor = neighbour

        self.model.grid.move_agent(self, closest_neighbor)

    def apparent_wealth(self):
        return None

    def move_to_wealth(self):
        # Agents move towards targets with higher apparent wealth
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
                neighbours_surrounding = self.model.grid.get_neighborhood(
                    surrounding_cell, True
                )

                # Get apparent wealth of each neighbour
                apparent_wealth = []
                for neighbour in neighbours_surrounding:
                    contents = self.model.grid.get_cell_list_contents([neighbour])
                    filter_tiles = [
                        agent
                        for agent in contents
                        if not isinstance(agent, heatmap.HeatmapTile)
                    ]

                    for content in filter_tiles:
                        if content.__class__.__name__ == "Target":
                            apparent_wealth.append(content.get_wealth())

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
                selected_neighbour = random.choice(empty_neighbours)

            self.model.grid.move_agent(self, selected_neighbour)

    def perceived_police(self):
        # Biased movement of thieves when there is perceived police presence in the model
        pass

    def police_patrol_move(self):
        # Police have a patrol route, with a fixed pattern
        # Get neighbours (Moore neighbourhood)
        neighbours = self.model.grid.get_neighborhood(self.pos, True)

        grid_height = self.model.grid.height

        x, y = map(int, self.pos)

        # Movement up
        if self.direction == 1: 
            # Flip direction if at top of grid
            if y + 1 >= grid_height:
                self.direction = -1
                return

            # Check if the cell above is empty
            if (x, y + 1) in neighbours:
                contents = self.model.grid.get_cell_list_contents([(x, y + 1)])
                filter_tiles = [
                    agent for agent in contents if not isinstance(agent, heatmap.HeatmapTile)
                ]
                # Move if cell is empty
                if len(filter_tiles) == 0:
                    self.model.grid.move_agent(self, (x, y + 1))
                    return

        elif self.direction == -1:
            # Flip direction if at bottom of grid
            if y - 1 < 0:
                self.direction = 1
                return

            # Check if the cell below is empty
            if (x, y - 1) in neighbours:
                contents = self.model.grid.get_cell_list_contents([(x, y - 1)])
                filter_tiles = [
                    agent for agent in contents if not isinstance(agent, heatmap.HeatmapTile)
                ]
                # Move if cell is empty
                if len(filter_tiles) == 0:
                    self.model.grid.move_agent(self, (x, y - 1))
                    return

    def get_wealth(self):
        raise NotImplementedError

    def get_attentiveness(self):
        raise NotImplementedError

    def was_robbed(self):
        raise NotImplementedError

    def get_vision_radius(self):
        return self.vision_radius

    def get_local_business(self) -> float:
        return self.model.get_local_business(self.pos)
        # return 0
