from pack_of_cards import PackOfCards
from table import GameTable
from player import Player
from card import Card
import socket
import config


def can_put_card(card, upper_card, current_color):
    if card.face_value == 14 or card.face_value == 13:
        return True
    if card.color != current_color and card.face_value != upper_card.face_value:
        return False
    return True


def can_pass_turn(hand, upper_card, current_color):
    for card in hand:
        if (card.color == current_color or card.face_value == upper_card.face_value or
                    card.face_value == 14 or card.face_value == 13):
            return False
    return True


class GameException(Exception):
    def __init__(self, mess):
        self.mess = mess


class Arbiter:
    def __init__(self):
        self._pack_of_cards = PackOfCards()
        self.table = GameTable(config.PLAYERS_NUMBER)
        self.socket = self._make_connection()
        self.players = []
        self._game_over = False

    def run_game(self):
        for player in self.players[1:]:
            for i in range(4):
                player.hand.add(self._pack_of_cards.get_card())

        for i in range(3):
            self.players[0].hand.add(self._pack_of_cards.get_card())

        first_card = self._pack_of_cards.get_card()
        while first_card.face_value in {10, 11, 12, 13, 14}:
            self._pack_of_cards.add_card(first_card)
            first_card = self._pack_of_cards.get_card()

        self.table.upper_card = first_card
        self.table.current_color = self.table.upper_card.color

        self.table.current_player = (self.table.current_player + 1) % self.table.players_number

        turn_params = {"message": "Your turn", "players_req": 0}
        for player_num in range(len(self.players)):
            game_position = self._create_map(player_num)
            self.players[player_num].change_game_state(game_position)
        while not self._game_over:
            turn_params = self._make_turn(turn_params)
        self._complete_game()

    def _get_next_player(self):
        return (self.table.players_number + self.table.current_player + self.table.clockwise) \
               % self.table.players_number

    def _get_used_cards(self):
        cards = set()
        for player in self.players:
            for card in player.hand:
                cards.add(card)
        cards.add(self.table.upper_card)
        return cards

    def _draw_card(self, players_req):
        if players_req > 0:
            raise GameException("You draw cards enough, please, put card or pass turn!")
        card = self._pack_of_cards.get_card()
        if card is None:
            cards = self._get_used_cards()
            self._pack_of_cards.create_new_pack(cards)
            card = self._pack_of_cards.get_card()
            if card is None:
                raise GameException("The pack has no more cards")
        self.players[self.table.current_player].hand.add(card)

    def check_card_in_hand(self, card):
        if card not in self.players[self.table.current_player].hand:
            return False
        else:
            return True

    def _add_next_player_cards(self, count):
        for i in range(count):
            new_card = self._pack_of_cards.get_card()
            self.players[self._get_next_player()].hand.add(new_card)

    def _put_card(self, card):
        if not can_put_card(card, self.table.upper_card, self.table.current_color):
            raise GameException("You can't put this card, please, choice another")

        if not self.check_card_in_hand(card):
            raise GameException("You haven't this card!!!")

        self.players[self.table.current_player].hand.remove(card)

        after_next = (self.table.players_number + self.table.current_player +
                  2 * self.table.clockwise) % self.table.players_number

        if card.face_value == 12:
            self._add_next_player_cards(2)
            self.table.current_player = after_next

        elif card.face_value == 11:
            self.table.change_clockwise()
            self.table.current_player = self._get_next_player()

        elif card.face_value == 10:
            self.table.current_player = after_next

        else:
            self.table.current_player = self._get_next_player()

        self.table.lay_on(card)
        if card.color != 5:
            self.table.current_color = card.color

    def _change_color(self, face, color):
        if not can_put_card(Card(face, 4), self.table.upper_card, self.table.current_color):
            raise GameException("You can't put this card, please, choice another")
        unnext = (self.table.players_number + self.table.current_player +
                  2 * self.table.clockwise) % self.table.players_number

        if not self.check_card_in_hand(Card(face, 4)):
            raise GameException("You haven't this card!!!")

        self.players[self.table.current_player].hand.remove(Card(face, 4))

        if face == 13:
            self._add_next_player_cards(4)
            self.table.current_player = unnext
        else:
            self.table.current_player = self._get_next_player()

        self.table.lay_on(Card(face, 4))
        self.table.current_color = color

    def _pass_turn(self, players_req):
        if players_req == 0:
            raise GameException("Firstly, you mast draw a card")
        if not can_pass_turn(self.players[self.table.current_player].hand, self.table.upper_card,
                             self.table.current_color):
            raise GameException("You can't pass turn, you have the right cards")
        self.table.current_player = self._get_next_player()

    def _create_map(self, player_num):
        game_position = {"goal": 0, "hand": [{'face_value': card.face_value, 'color': card.color}
                                             for card in self.players[player_num].hand],
                         "who's_turn": self.table.current_player,
                         "direction": self.table.clockwise, "color": self.table.current_color,
                         "up_card": self.table.upper_card.face_value, "players": [], "_game_over": self._game_over}

        for i in range(0, self.table.players_number):
            game_position["players"].append({
                "name": self.players[i].name,
                "num": len(self.players[i].hand)
            })
        return game_position

    def _complete_game(self):
        if self._game_over:
            for player_num in range(len(self.players)):
                game_position = self._create_map(player_num)
                self.players[player_num].change_game_state(game_position)

    def _make_turn(self, turn_params):
        turn_info = self.players[self.table.current_player].make_turn(turn_params["message"])
        try:
            if turn_info["method"] == "pass_turn":
                self._pass_turn(turn_params["players_req"])
                turn_params["players_req"] = 0

            elif turn_info["method"] == "draw_card":
                self._draw_card(turn_params["players_req"])
                turn_params["players_req"] += 1

            elif turn_info["method"] == "change_color":
                self._change_color(turn_info["card"], turn_info["color"])
                turn_params["players_req"] = 0

            elif turn_info["method"] == "put_card":
                self._put_card(Card(turn_info["card"], turn_info["color"]))
                turn_params["players_req"] = 0
            else:
                raise GameException("incorrect command")

            self._game_over = self._check_for_over()
            for player_num in range(len(self.players)):
                game_position = self._create_map(player_num)
                self.players[player_num].change_game_state(game_position)
            turn_params["message"] = "Your turn"
        except GameException as e:
            if 'method' not in turn_info:
                turn_params["players_req"] += 1
            turn_params["message"] = e.mess
        return turn_params

    def wait_players(self):
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
        s.bind(("0.0.0.0", 4000))
        s.listen(self.table.players_number)
        return s

    def _check_for_over(self):
        for player in self.players:
            if len(player.hand) == 0:
                return True
        return False