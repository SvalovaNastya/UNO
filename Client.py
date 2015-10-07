import argparse
import socket
import json
from ConsoleUserInterface import CUI


game_table = {}
ui = None


def parse_args():
    parser = argparse.ArgumentParser(prefix_chars='-/')
    parser.add_argument('server_ip', type=str, default='127.0.0.1')
    parser.add_argument('server_port', type=int, default=4000)
    parser.add_argument('name', type=str)
    return parser.parse_args()


def run_game(conn):
    while True:
        mess = conn.recv(1024)
        mess = json.loads(mess.decode("utf-8"), "utf-8")
        if mess["goal"] == 1:
            s, face, color = ui.make_step(mess['message'])
            if s == 's':
                ans = {'method': "put_card", 'card': face, 'color': color}
            elif s == "cc":
                ans = {'method': "change_color", 'card': face, 'color': color}
            elif s == 'pass':
                ans = {'method': "pass_step"}
            elif s == 'draw':
                ans = {'method': "draw_card"}
            else:
                raise Exception("wtf!")
            a = json.dumps(ans)
            conn.sendall(a.encode())
        elif mess["goal"] == 0:
            # print(mess)
            ui.write_table(mess["players"], mess["whos_step"], mess["hand"], mess["direction"], mess["color"],
                           mess["up_curd"], mess["game_over"])


if __name__ == "__main__":
    args = parse_args()
    conn = socket.socket()
    conn.connect((args.server_ip, args.server_port))
    ui = CUI(args.name)
    conn.send(args.name.encode('utf-8'))
    print("вы подключились к серверу")
    run_game(conn)