import sys
import time

board_size = 16
colors = True

def piece_string(team, id):
    return '%s%3d' % (team, id)

def clear():
    for i in range(board_size + 1):
        sys.stdout.write("\033[F")  # back to previous line
        sys.stdout.write("\033[K")  # clear line

def view_board(board):
    new_board = ''
    for i in range(board_size):
        for j in range(board_size):
            if board[i][j]:
                new_board += '['
                if colors:
                    if board[i][j][0] == 'W':
                        new_board += '\033[1m\u001b[37m'
                    else:
                        new_board += '\033[1m\u001b[36m'
                new_board += piece_string(board[i][j][0], board[i][j][1])
                if colors:
                    new_board += '\033[0m\u001b[0m'
                new_board += '] '
            else:
                new_board += '[    ] '
        new_board += '\n'
    print(new_board)
    return new_board


def play(board_states, delay=0.1):
    print('')
    for state_index in range(len(board_states)):
        view_board(board_states[state_index])
        time.sleep(delay)
        clear()


def parse_txt(filename):
    file = open(filename, "r")
    lines = [line.strip() for line in file]
    start = lines.index("")
    print("Starting line: ", start)
    idx = start + 1
    boards = []
    while idx < len(lines) - board_size:
        board = []
        for i in range(board_size):
            line = lines[idx]
            spots = [line[i:i+7].strip() for i in range(0, len(line), 7)]
            assert(len(spots) == board_size)
            row = []
            for spot in spots:
                if spot[1] == ' ':
                    row.append(None)
                    continue
                team = spot[1]
                num = int(spot[2:5])
                row.append((team, num))
            board.append(row)
            idx += 1
        boards.append(board)
        idx += 1
    return boards

boards = parse_txt("kryptonite.txt")
print(len(boards))
play(boards)