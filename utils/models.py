import rich

class Task:
    
    def __init__(self, id, name, priority, due, done):
        self.id = id
        self.name = name
        self.priority = priority
        self.due = due
        self.done = done == 1

    @classmethod
    def create_from_db(cls, database_repr):
        return Task(*database_repr)
    
    def __repr__(self):
        return f"Task({self.id}, {self.name}, {self.priority}, {self.due}, {self.done})"

    def __str__(self):
        return self.__repr__()