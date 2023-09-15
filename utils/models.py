from datetime import datetime

class Task:
    
    def __init__(self, name, priority, due, done=False, time_created=None):
        self.id = None
        self.name = name
        self.priority = priority
        self.due = due
        self.done = (done == 1)

        self.time_created = time_created if time_created else datetime.min

    @classmethod
    def create_from_db(cls, database_repr):
        t = Task(*(database_repr[1:]))
        t.id = database_repr[0]
        return t
    
    def __repr__(self):
        return f"Task(id={self.id}, name='{self.name}', priority={self.priority}, due'{self.due}', done='{self.done}', created='{self.time_created}')"

    def __str__(self):
        return self.__repr__()