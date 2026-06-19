import mesa


class HeatmapTile(mesa.Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        self.pos = pos

    def step(self):
        x, y = self.pos

        # Decrease the crime count by a fraction every timestep (e.g., 0.1)
        # This allows smooth transitioning down through your color brackets
        if self.model.crime_heatmap[x][y] > 0:
            self.model.crime_heatmap[x][y] = max(
                0, self.model.crime_heatmap[x][y] - 0.1
            )

        # Once the crime count completely cools down to 0, remove the tile
        if self.model.crime_heatmap[x][y] == 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
