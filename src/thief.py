import mesa
from person import Person
from base_model import BaseModel


class Thief(Person):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


if __name__ == "__main__":
    model = BaseModel()
    thief = Thief(1, model)