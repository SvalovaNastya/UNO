from PackOfCards import PackOfCards
from Table import GameTable
from Player import Player
import Json
import socket


def can_put_card(card, upper_card, current_color):
    if card.face_value == 14 or card.face_value == 13:
        return True
    if card.color != current_color or card.face_value != upper_card.face_value:
        return False
    return True


def can_pass_step(hand, upper_card, current_color):
    for card in hand:
        if (card.color == current_color or card.face_value == upper_card.face_value or
                    card.face_value == 14 or card.face_value == 13):
            return False
        else:
            return True

class GameException(Exception):
    def __init__(self, mess):
        super.__init__(mess)


class Arbiter:
    def __init__(self, players_number):
        self.pack_of_cards = PackOfCards()
        self.table = GameTable(players_number, self.pack_of_cards)
        self.socket = self._make_connection()
        self.players = self._wait_players()
        self.game_over = False

    def game(self):
        while not self.game_over:
            self._make_step()

    # 10 - пропуск хода
    #11 - реверс
    #12 - +2
    #13 - +4
    #14 - смена цвета

    def draw_card(self, players_req):
        if players_req > 0:
            raise GameException("Больше нельзя взять карт, вы должны пропустить ход")
        card = self.pack_of_cards.get_card()
        if card == None:
            cards = self.table.pick_cards()
            self.pack_of_cards.add_cards(cards)
            card = self.pack_of_cards.get_card()
            if card == None:
                raise GameException("В колоде больше нет карт")
        self.players[self.table.current_player].hand.add(card)

    def put_card(self, card):
        if not can_put_card(card, self.table.upper_card, self.table.current_color):
            raise GameException("Эту карту нельзя положить, выберете другую")
        next = (self.table.players_number + self.table.current_player + self.table.clockwise) \
               % self.table.players_number
        unnext = (self.table.players_number + self.table.current_player +
                  2 * self.table.clockwise) % self.table.players_number

        if card.face_value == 12:
            for i in range(2):
                new_card = self.pack_of_cards.get_card()
                self.players[next].draw_cards(new_card)
            self.table.current_player = unnext

        elif card.face_value == 11:
            self.table.change_clockwise()
            self.table.current_player = next

        elif card.face_value == 10:
            self.table.current_player = unnext

        else:
            self.table.current_player = next

        self.table.lay_on(card)
        if card.color != 5:
            self.table.current_color = card.color

    def change_color(self, card, color):
        if not can_put_card(card, self.table.upper_card, self.table.current_color):
            raise GameException("Эту карту нельзя положить, выберете другую")
        next = (self.table.players_number + self.table.current_player + self.table.clockwise) \
               % self.table.players_number
        unnext = (self.table.players_number + self.table.current_player +
                  2 * self.table.clockwise) % self.table.players_number

        if card.face_value == 13:
            for i in range(4):
                new_card = self.pack_of_cards.get_card()
                self.players[next].draw_cards(new_card)
            self.table.current_player = unnext
        else:
            self.table.current_player = next
        self.table.current_color = color

    def pass_step(self, players_req):
        if players_req == 0:
            raise GameException("Вы должны сначала взять карту")
        if not can_pass_step(self.players[self.table.current_player].hand, self.table.upper_card, self.table.current_color):
            raise GameException("Вы не можете пропустить ход, у вас есть нужные карты")
        next = (self.table.players_number + self.table.current_player + self.table.clockwise) \
               % self.table.players_number
        self.table.current_player = next

    def create_map(self, player_num):
        map = {}
        map["hand"] = self.players[player_num].hand
        map["players"] = [len(self.players[i].hand) for i in range(
            self.players[(player_num + self.table.players_number + 1) % self.table.players_number],
            self.players[(player_num + self.table.players_number - 1) % self.table.players_number])]
        map["up_curd"] = (self.table.upper_card.face_value, self.table.upper_card.color)
        return map

    def _make_step(self):
        message = "Ваш ход"
        players_req = 0
        while True:
            method = self.players[self.table.current_player].make_step(message)
            try:
                if len(method) == 0:
                    method[0](players_req)
                if len(method) == 1:
                    method[0](method[1])
                if len(method) == 2:
                    method[0](method[1], method[2])
                for player_num in range(len(self.players)):
                    map = self.create_map(player_num)
                    map = Json.dump(map)
                    self.players[player_num].change_game_state(map)
                message = "Ваш ход"
                players_req = 0
            except GameException as e:
                if len(method) == 0:
                    players_req += 1
                message = e

    def _wait_players(self):
        players = []
        for i in range(self.table.players_number):
            conn, _ = self.socket.accept()
            players.append(Player(conn))
        return players

    def _make_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect(("gmail.com", 80))
        print("your address: " + s.getsockname()[0])
        s.bind(("", 4000))
        s.listen(self.table.players_number)
        return s