from PackOfCards import PackOfCards
from Table import GameTable
from Player import Player
from Card import Card
import json
import socket


def can_put_card(card, upper_card, current_color):
    if card.face_value == 14 or card.face_value == 13:
        return True
    if card.color != current_color and card.face_value != upper_card.face_value:
        return False
    return True


def can_pass_step(hand, upper_card, current_color):
    for card in hand:
        if (card.color == current_color or card.face_value == upper_card.face_value or
                    card.face_value == 14 or card.face_value == 13):
            return False
    return True


class GameException(Exception):
    def __init__(self, mess):
        self.mess = mess


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

    def get_next_player(self):
        return (self.table.players_number + self.table.current_player + self.table.clockwise) \
               % self.table.players_number

    def draw_card(self, players_req):
        if players_req > 0:
            raise GameException("Больше нельзя взять карт, вы должны пропустить ход")
        card = self.pack_of_cards.get_card()
        if card is None:
            cards = self.table.pick_cards
            print("Карты из колоды взялись! Ура")
            self.pack_of_cards.add_cards(cards)
            card = self.pack_of_cards.get_card()
            if card is None:
                raise GameException("В колоде больше нет карт")
        self.players[self.table.current_player].hand.add(card)

    def check_card_in_hand(self, card):
        if card not in self.players[self.table.current_player].hand:
            return False
        else:
            return True

    def put_card(self, card):
        if not can_put_card(card, self.table.upper_card, self.table.current_color):
            raise GameException("Эту карту нельзя положить, выберете другую")

        if not self.check_card_in_hand(card):
            raise GameException("У вас нет такой карты!!!")

        self.players[self.table.current_player].hand.remove(card)

        unnext = (self.table.players_number + self.table.current_player +
                  2 * self.table.clockwise) % self.table.players_number

        if card.face_value == 12:
            for i in range(2):
                new_card = self.pack_of_cards.get_card()
                self.players[self.get_next_player()].hand.add(new_card)
            self.table.current_player = unnext

        elif card.face_value == 11:
            self.table.change_clockwise()
            self.table.current_player = self.get_next_player()

        elif card.face_value == 10:
            self.table.current_player = unnext

        else:
            self.table.current_player = self.get_next_player()

        self.table.lay_on(card)
        if card.color != 5:
            self.table.current_color = card.color

    def change_color(self, face, color):
        if not can_put_card(Card(face, 4), self.table.upper_card, self.table.current_color):
            raise GameException("Эту карту нельзя положить, выберете другую")
        unnext = (self.table.players_number + self.table.current_player +
                  2 * self.table.clockwise) % self.table.players_number

        if not self.check_card_in_hand(Card(face, 4)):
            raise GameException("У вас нет такой карты!!!")

        self.players[self.table.current_player].hand.remove(Card(face, 4))

        if face == 13:
            for i in range(4):
                new_card = self.pack_of_cards.get_card()
                self.players[self.get_next_player()].hand.add(new_card)
            self.table.current_player = unnext
        else:
            self.table.current_player = self.get_next_player()

        self.table.lay_on(Card(face, 4))
        self.table.current_color = color

    def pass_step(self, players_req):
        if players_req == 0:
            raise GameException("Вы должны сначала взять карту")
        if not can_pass_step(self.players[self.table.current_player].hand, self.table.upper_card,
                             self.table.current_color):
            raise GameException("Вы не можете пропустить ход, у вас есть нужные карты")
        self.table.current_player = self.get_next_player()

    def create_map(self, player_num):
        game_position = {"goal": 0, "hand": [{'face_value': card.face_value, 'color': card.color}
                                             for card in self.players[player_num].hand],
                         "who's_step": self.table.current_player,
                         "direction": self.table.clockwise, "color": self.table.current_color,
                         "up_curd": self.table.upper_card.face_value, "players": [], "game_over": self.game_over}

        for i in range(0, self.table.players_number):
            game_position["players"].append({
                "name": self.players[i].name,
                "num": len(self.players[i].hand)
            })
        return game_position

    def _make_step(self):
        self.table.upper_card = self.pack_of_cards.get_card()  # TODO: проверить на то, не сменит ли она цвет
        self.table.current_color = self.table.upper_card.color
        for player in self.players:
            for i in range(4):
                player.hand.add(self.pack_of_cards.get_card())
        message = "Ваш ход"
        players_req = 0
        for player_num in range(len(self.players)):
            game_position = self.create_map(player_num)
            game_position = json.dumps(game_position)
            self.players[player_num].change_game_state(game_position)
        while True:
            method = self.players[self.table.current_player].make_step(message)
            try:
                if method[0] == "pass_step":
                    self.pass_step(players_req)
                    players_req = 0

                elif method[0] == "draw_card":
                    self.draw_card(players_req)
                    players_req += 1

                elif method[0] == "change_color":
                    self.change_color(method[1], method[2])
                    players_req = 0

                elif method[0] == "put_card":
                    self.put_card(Card(method[1], method[2]))
                    players_req = 0
                else:
                    raise GameException("incorrect command")

                self.game_over = self.check_for_over()
                for player_num in range(len(self.players)):
                    game_position = self.create_map(player_num)
                    game_position = json.dumps(game_position)
                    self.players[player_num].change_game_state(game_position)
                message = "Ваш ход"
                if self.game_over:
                    for player_num in range(len(self.players)):
                        game_position = self.create_map(player_num)
                        game_position = json.dumps(game_position)
                        self.players[player_num].change_game_state(game_position)
                    print("dddd")
                    break
            except GameException as e:
                if len(method) == 0:
                    players_req += 1
                message = e.mess

    def _wait_players(self):
        players = []
        for i in range(self.table.players_number):
            conn, _ = self.socket.accept()
            name = conn.recv(1024).decode('utf-8')
            print("игрок {0} подключился".format(name))
            players.append(Player(conn, name))
        return players

    def _make_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # s.connect(("gmail.com", 80))
        # print("your address: " + s.getsockname()[0])
        s.bind(("0.0.0.0", 4000))
        s.listen(self.table.players_number)
        return s

    def check_for_over(self):
        for player in self.players:
            if len(player.hand) == 0:
                return True
        return False