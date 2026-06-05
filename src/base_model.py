import mesa


class BaseModel(mesa.Model):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    model = BaseModel()