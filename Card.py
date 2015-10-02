class Card:
    def __init__(self, face_value, color):
        self.face_value = face_value
        self.color = color

    def __hash__(self):
        return hash(self.face_value) ^ hash(self.color)

    def __eq__(self, other):
        return self.face_value == other.face_value and self.color == other.color
