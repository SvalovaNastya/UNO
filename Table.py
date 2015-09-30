class GameTable:
    def __init__(self, players_number, pack_of_cards):
        self.players_number = players_number
        self.pack_of_cards = pack_of_cards
        self.card_on_table = set()
        self.upper_card = None
        self.current_color = None
        self.current_player = 0
        self.clockwise = 1

    def lay_on(self, card):
        self.card_on_table.add(self.upper_card)
        self.upper_card = card

    def pick_cards(self):
        p = [card for card in self.pack_of_cards]
        self.pack_of_cards = set()
        return p

    def change_clockwise(self):
        self.clockwise *= -1