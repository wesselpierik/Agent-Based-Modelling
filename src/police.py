import mesa
from person import Person
# from base_model import BaseModel


class Police(Person):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
    
    def step(self):
        self.move()

    def get_attentiveness(self):
        return 1


if __name__ == "__main__":
    model = BaseModel()
    police = Police(1, model)
