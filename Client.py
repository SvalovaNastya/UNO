import argparse
import socket
import json
from console_user_interface import CUI
from socket_sender import SocketSender


game_table = {}
ui = None


def parse_args():
    parser = argparse.ArgumentParser(prefix_chars="-/")
    parser.add_argument("name", type=str)
    parser.add_argument("server_ip", nargs="?", type=str, default="127.0.0.1")
    parser.add_argument("server_port", nargs="?", type=int, default=4000)
    return parser.parse_args()


def run_game(connect):
    while True:
        mess = SocketSender.recv_all(connect)
        mess = json.loads(mess.decode("utf-8"), "utf-8")
        if mess["goal"] == 1:
            s, face, color = ui.make_turn(mess["message"])
            if s == "s":
                ans = {"method": "put_card", "card": face, "color": color}
            elif s == "cc":
                ans = {"method": "change_color", "card": face, "color": color}
            elif s == "pass":
                ans = {"method": "pass_turn"}
            elif s == "draw":
                ans = {"method": "draw_card"}
            else:
                raise Exception("wtf!")
            a = json.dumps(ans)
            SocketSender.send_all(connect, a.encode("utf-8"))
        elif mess["goal"] == 0:
            ui.write_table(mess["players"], mess["who's_turn"], mess["hand"], mess["direction"], mess["color"],
                           mess["up_card"], mess["_game_over"])
            if mess["_game_over"]:
                break


if __name__ == "__main__":
    args = parse_args()
    conn = socket.socket()
    conn.connect((args.server_ip, args.server_port))
    ui = CUI(args.name)
    conn.send(args.name.encode("utf-8"))
    print("вы подключились к серверу")
    run_game(conn)