import mesa
from person import Person
import numpy as np

# from base_model import BaseModel


class Police(Person):
    def __init__(
        self, unique_id: int, model, pos: tuple[int, int], vision_radius: int
    ) -> None:
        super().__init__(unique_id, model, pos, vision_radius)
        self.attentiveness = self.model.get_police_attentiveness()

        # Choose initial moving direction, 1 for up, -1 for down
        self.direction = np.random.choice([-1, 1])

        # Choose initial moving direction, 1 for up, -1 for down
        self.direction = np.random.choice([-1, 1])

    def step(self):
        self.police_patrol_move() # Change to self.police_patrol_move() for patrol movement

    def get_attentiveness(self):
        return self.attentiveness

    def police_patrol_move(self):
        return super().police_patrol_move()
