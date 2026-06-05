import mesa
import base_model


class Person(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        self.model = model


if __name__ == "__main__":
    model = base_model.BaseModel()
    person = Person(1, model)
