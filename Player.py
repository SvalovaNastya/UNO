import Json


class Player:
    def __init__(self, socket):
        self.hand = set()
        self.socket = socket

    def make_step(self, message):
        self.socket.sendall(message)
        data = self.socket.recv(2048)
        method_dict = Json.loads(data)
        method = []
        method[0] = method_dict["method"]
        if "card" in method_dict:
            method[1] = method_dict["card"]
        if "color" in method_dict:
            method[2] = method_dict["clor"]
        return method

    def change_game_state(self, game_state):
        self.socket.sendall(game_state)