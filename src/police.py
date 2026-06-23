import mesa
from person import Person

# from base_model import BaseModel


class Police(Person):
    def __init__(
        self, unique_id: int, model, pos: tuple[int, int], vision_radius: int
    ) -> None:
        super().__init__(unique_id, model, pos, vision_radius)
        self.attentiveness = self.model.get_police_attentiveness()

    def step(self):
        self.move()

    def get_attentiveness(self):
        return self.attentiveness
