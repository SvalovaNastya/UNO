import random
from card import Card


class PackOfCards:
    def __init__(self):
        self._number = 108
        self._cards_in_pack = self.create_new_pack(set())
        self.card_colors = {0: 'red', 1: 'green', 2: 'yellow', 3: 'blue', 4: 'black'}

    @staticmethod
    def create_new_pack(exclusion_cards):
        pack = []
        for color in range(4):
            for face_value in range(13):
                pack.append(Card(face_value, color))
                if face_value != 0:
                    card = Card(face_value, color)
                    if card not in exclusion_cards:
                        pack.append(card)
        for face_value in range(13, 15):
            for _ in range(4):
                card = Card(face_value, 4)
                if card not in exclusion_cards:
                    pack.append(card)
        random.shuffle(pack)
        return pack

    def get_card(self):
        if len(self._cards_in_pack) == 0:
            return None
        return self._cards_in_pack.pop()

    def add_card(self, card):
        if card not in self._cards_in_pack:
            self._cards_in_pack.append(card)