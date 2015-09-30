import random


class PackOfCards:
    def __init__(self):
        self._number = 108
        self._pack_of_card = self._create_cards()
        self.card_colors = {0: 'red', 1: 'green', 2: 'yellow', 3: 'blue', 4: 'black'}
        self._not_used_cards = set()
        self._rand = random.Random()

    @staticmethod
    def _create_cards():
        pack = []
        for color in range(4):
            for face_value in range(14):
                pack.append(Card(face_value, color))
                if face_value != 0:
                    pack.append(Card(face_value, color))
        for face_value in range(14, 16):
            for _ in range(4):
                pack.append(Card(face_value, 4))
        return pack

    def get_card(self):
        if len(self._not_used_cards) == 0:
            return None
        while True:
            index = self._rand.next(self._number)
            if self._pack_of_card[index] in self._not_used_cards:
                return self._pack_of_card[index]

    def add_cards(self, cards):
        for card in cards:
            self._not_used_cards.add(card)


class Card:
    def __init__(self, face_value, color):
        self.face_value = face_value
        self.color = color
