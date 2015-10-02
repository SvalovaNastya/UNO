import json


class Player:
    def __init__(self, socket, name):
        self.hand = set()
        self.socket = socket
        self.name = name

    def make_step(self, message):
        ans = {}
        ans["goal"] = 1
        ans["message"] = message
        ans = json.dumps(ans)
        self.socket.sendall(ans.encode('utf-8'))
        data = self.socket.recv(1024)
        method_dict = json.loads(data.decode("utf-8"))
        method = []
        method.append(method_dict["method"])
        if "card" in method_dict:
            method.append(method_dict["card"])
        if "color" in method_dict:
            method.append(method_dict["color"])
        return method

    def change_game_state(self, game_state):
        self.socket.sendall(game_state.encode('utf-8'))