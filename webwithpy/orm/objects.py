class Field:
    def __init__(self, field_name, field_type: str):
        self.name = field_name
        self.type = field_type

    def __getattribute__(self, item):
        try:
            super(Field, self).__getattribute__(item)
        except AttributeError as e:
