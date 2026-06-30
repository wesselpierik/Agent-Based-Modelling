from person import Person
import numpy as np
import heatmap

# from base_model import BaseModel


class Police(Person):
    def __init__(
        self, unique_id: int, model, pos: tuple[int, int], vision_radius: int
    ) -> None:
        super().__init__(unique_id, model, pos, vision_radius)
        self._attentiveness = self.model.get_police_attentiveness()

        # Choose initial moving direction, 1 for up, -1 for down
        self.direction = np.random.choice([-1, 1])

    def step(self):
        self.police_patrol_move()  # Change to self.police_patrol_move() for patrol movement

    def get_attentiveness(self):
        return self._attentiveness

    def police_patrol_move(self) -> None:
        """
        Implements patrol movement (up and down) used for police
        """
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
                    agent
                    for agent in contents
                    if not isinstance(agent, heatmap.HeatmapTile)
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
                    agent
                    for agent in contents
                    if not isinstance(agent, heatmap.HeatmapTile)
                ]
                # Move if cell is empty
                if len(filter_tiles) == 0:
                    self.model.grid.move_agent(self, (x, y - 1))
                    return
