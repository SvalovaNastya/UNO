class GameTable:
    def __init__(self, players_number):
        self.players_number = players_number
        self.upper_card = None
        self.current_color = None
        self.current_player = 0
        self.clockwise = 1

    def lay_on(self, card):
        self.upper_card = card

    def change_clockwise(self):
        self.clockwise *= -1