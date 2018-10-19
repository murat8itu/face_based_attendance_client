class Student(object):
    id = 0
    full_name = ""
    email = ""

    def __init__(self):
        self.id = 0
        self.full_name = ""
        self.email = ""

    def __hash__(self):
        return hash((self.id, self.full_name, self.email))

    def __str__(self):
        return str(self.id) + ' ' + self.full_name + ' ' + self.email
