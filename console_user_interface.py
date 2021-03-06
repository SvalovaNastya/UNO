
class CUI:
    def __init__(self, my_name):
        self.my_name = my_name
        self.colors = {0: 'red', 1: 'green', 2: 'yellow', 3: 'blue', 4: 'black'}
        self.faces = {0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "pass_turn", 11: "revers",
                 12: "+2", 13: "+4", 14: "change_color"}

        self.input_colors = {'r': 0, 'g': 1, 'y': 2, 'b': 3, 'k': 4}
        self.input_faces = {"0": 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'p': 10, 'r': 11,
                       't': 12, 'f': 13, 'c': 14}

    def write_table(self, participants, whos_turn, my_hand, direction, color, card, game_over):
        s = ''
        for i in range(len(participants)):
            s += participants[i]["name"] + ': ' + str(participants[i]["num"])
            s += '; '
        s += '\n'
        s += 'turn: ' + participants[whos_turn]["name"] + '\n'
        s += 'upper: ' + self.faces[card] + '\n'
        s += 'color: ' + self.colors[color] + '\n'
        s += 'direction: '
        if direction == 1:
            s += "clockwise\n"
        else:
            s += "anticlockwise\n"
        s += 'my_hand' + '\n'
        for card in my_hand:
            s += '(' + self.faces[card["face_value"]] + ' ' + self.colors[card["color"]] + ") "
        if game_over:
            s += "game over"
        s += '\n'
        print(s)


    def make_turn(self, message):
        print(message)
        while True:
            str = input()
            if str == 'help' or str == 'h':
                print("write face value and color from your hand or require one more card \n \
                    colors : r - red, g - green, y - yellow, b - blue, k - black \n \
                    face values: 0-9, p - pass turn, r - revers, t - +2, f - +4, c - change color \n \
                    for instance : 0r or pass or draw")
            if str == 'pass' or str == "draw":
                return str, None, None
            if len(str) == 0:
                continue
            elif str[0] == 'f' or str[0] == 'c':
                mess = "what color you want?"
                while True:
                    m = input(mess)
                    if m not in self.input_colors:
                        mess = "this color doesn't exist, chose another color, please"
                        continue
                    return "cc", self.input_faces[str[0]], self.input_colors[m]
            if len(str) != 2:
                print("error input print 'help'\n")
                continue
            if str[0] not in self.input_faces or str[1] not in self.input_colors:
                print('incorrect command, print "help" for correct command\n')
                continue
            return "s", self.input_faces[str[0]], self.input_colors[str[1]]