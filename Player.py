import json
from socket_sender import SocketSender


class Player:
    def __init__(self, socket, name):
        self.hand = set()
        self.socket = socket
        self.name = name

    def make_turn(self, message):
        ans = {"goal": 1, "message": message}
        ans = json.dumps(ans)

        ans = ans.encode('utf-8')
        SocketSender.send_all(self.socket, ans)

        data = SocketSender.recv_all(self.socket)
        return json.loads(data.decode("utf-8"))

    def change_game_state(self, game_state):
        game_state = json.dumps(game_state)
        game_state = game_state.encode('utf-8')
        SocketSender.send_all(self.socket, game_state)