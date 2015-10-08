import json
import struct
import SocketSender


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

        ans = ans.encode('utf-8')
        SocketSender.SocketSender.send_all(self.socket, ans)
        # n = len(message)
        # self.socket.sendall(struct.pack('I', n))
        # self.socket.sendall()

        data = SocketSender.SocketSender.recv_all(self.socket)
        # self.socket.recv(1024)
        method_dict = json.loads(data.decode("utf-8"))
        method = []
        method.append(method_dict["method"])
        if "card" in method_dict:
            method.append(method_dict["card"])
        if "color" in method_dict:
            method.append(method_dict["color"])
        return method

    def change_game_state(self, game_state):
        game_state = game_state.encode('utf-8')
        SocketSender.SocketSender.send_all(self.socket, game_state)
        # n = len(game_state)
        # self.socket.sendall(struct.pack('I', n))
        # self.socket.sendall(game_state.encode('utf-8'))