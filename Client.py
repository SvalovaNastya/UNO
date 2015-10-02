import argparse
import socket
import Json


game_table = {}
ui = None

def parse_args():
    parser = argparse.ArgumentParser(prefix_chars='-/')
    parser.add_argument('server_ip', type=str, default='127.0.0.1')
    parser.add_argument('server_port', type=int, default=4000)
    return parser.parse_args()


def run_game(conn):
    while True:
        mess = conn.recvall()
        mess = Json.load(mess)
        if mess["goal"] == 1:
            s, face, color = ui.make_step(mess['message'])
            if s == 's':
                if face == 14:
                    ans = {'method': "change_color"}
                else:
                    ans = {'method': "put_card", 'card': face, 'color': color}
            elif s == 'pass':
                ans = {'method': "pass_step"}
            else:
                ans = {'method': "draw_card"}
            a = Json.dump(ans)
            conn.sendall(a)
        elif mess["goal"] == 0:
            ui.write_table(mess["players"], mess["whos_step"], mess["hand"], mess["direction"], mess["color"], mess["up_curd"])




if __name__ == "__main__":

    args = parse_args()
    conn = socket.socket()
    conn.connect((args['server_ip'], args['server_port']))
    run_game(conn)