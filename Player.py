import json
import SocketSender


class Player:
    def __init__(self, socket, name):
        self.hand = set()
        self.socket = socket
        self.name = name

    def make_step(self, message):
        ans = {"goal": 1, "message": message}
        ans = json.dumps(ans)

        ans = ans.encode('utf-8')
        SocketSender.SocketSender.send_all(self.socket, ans)

        data = SocketSender.SocketSender.recv_all(self.socket)
        method_dict = json.loads(data.decode("utf-8"))
        method = [method_dict["method"]]
        if "card" in method_dict:
            method.append(method_dict["card"])
        if "color" in method_dict:
            method.append(method_dict["color"])
        return method

    def change_game_state(self, game_state):
        game_state = game_state.encode('utf-8')
        SocketSender.SocketSender.send_all(self.socket, game_state)