import random
from battlehack20.stubs import *

# TODO: If neighbor or neighbor's neighbor just pushed, then wait a bit
# TODO: Overlord spam a couple columns near the end (to try and win tiebreaker)

GAME_MAX = 250
FARTHEST_ROW = 11

DEBUG = 0
def dlog(str):
    if DEBUG > 0:
        log(str)


def ilog(str):
    if True:
        log(str)

def inbounds(r, c):
    if r < 0 or c < 0 or c >= board_size or r >= board_size:
        return False
    return True

def check_space_wrapper(r, c):
    # check space, except doesn't hit you with game errors
    if not inbounds(r, c):
        return False
    try:
        return check_space(r, c)
    except:
        return None

def spaces_in_front(a, b):
    diff = b - a
    return diff if team == Team.WHITE else -diff

def map_loc(loc):
    return loc if team == Team.WHITE else 15 - loc


team = get_team()
opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
board_size = get_board_size()


class Pawn:
    def __init__(self):
        self.team = get_team()
        self.forward = 1 if self.team == Team.WHITE else -1
        self.local_, self.prev_local_ = None, None
        self.waiting = 0
        self.board_size = get_board_size()


    def calc_local(self):
        board = []
        for rdiff in range(-2, 3):
            row = []
            for cdiff in range(-2, 3):
                row.append(self.check_piece_relative(rdiff, cdiff))
            board.append(row)
        return board


    def local(self, a, b):
        return self.local_[a + 2][b + 2]


    def prev_local(self, a, b):
        return self.prev_local_[a + 2][b + 2]


    def update_state(self):
        self.row, self.col = get_location()
        self.nextrow = self.row + self.forward
        self.prev_local_ = self.local_
        self.local_ = self.calc_local()
        if self.prev_local_ is None:
            self.prev_local_ = self.local_


    def check_piece_relative(self, rdiff, cdiff):
        return check_space_wrapper(self.row + rdiff * self.forward, self.col + cdiff)


    def run(self):
        self.update_state()
        if self.trycapture():
            return
        # CHARGE!!!!
#        timer = 16 - map_loc(self.row)
        if self.waiting > 4 and map_loc(self.row) < FARTHEST_ROW:
            self.tryforward()
            return
#        self.check_full()
        # Stay safe boi
        attackers, defenders, backup_defenders = self.danger()
        if defenders > attackers and backup_defenders > 0 and map_loc(self.row) < FARTHEST_ROW:
#        if defenders > attackers:
            self.tryforward()
        if attackers > 0:
            return
        if self.is_defending():
            return
        self.tryforward()
        bytecode = get_bytecode()
        dlog('Done! Bytecode left: ' + str(bytecode))
    

    def check_full(self):
        for rdiff in range(-2, 1):
            for cdiff in range(-2, 3):
                if not inbounds(self.row + rdiff, self.col + cdiff):
                    continue
                if self.local(rdiff, cdiff) == team:
                    continue
                self.waiting = 0
                return
        self.waiting = self.waiting + 1


    def is_defending(self):
        for cdiff in [-1, 1]:
            if self.local(1, cdiff) == team:
                for cdiff2 in [-1, 1]:
                    if self.local(2, cdiff + cdiff2) == opp_team:
                        return True
        return False

    def tryforward(self):
        if self.nextrow != -1 and self.nextrow != board_size and not check_space_wrapper(self.nextrow, self.col):
            move_forward()
            dlog('Moved forward!')


    def danger(self):
        attackers = 0
        defenders = 0
        backup_defenders = 0
        for cdiff in [-1, 1]:
            if check_space_wrapper(self.nextrow + self.forward, self.col + cdiff) == opp_team: # attacker positions
                attackers += 1
            if check_space_wrapper(self.nextrow - self.forward, self.col + cdiff) == team: # defending positions
                defenders += 1
            if check_space_wrapper(self.nextrow - self.forward * 2, self.col + cdiff) == team: # defending positions
                backup_defenders += 1
        return attackers, defenders, backup_defenders

    def check_safe_capture(self, dir):
        if self.local(0, dir*2) != team and self.local(-1, 0) != team and self.local(-1, -1) == team and self.local(1, -1) == team:
            log("Unsafe capture")
            return False
        return True


    def trycapture(self):
        # try catpuring pieces
        for cdiff in [-1, 1]:
            if self.local(1, cdiff) == opp_team:
                if self.check_safe_capture(cdiff):
                    capture(self.nextrow, self.col + cdiff)
                    return True
        return False

class Overlord:
    def __init__(self):
        self.team = get_team()
        log("Snakes and Ladders")
        self.forward = 1 if self.team == Team.WHITE else -1
        self.board_size = get_board_size()
        self.index = 0 if self.team == Team.WHITE else self.board_size - 1
        self.opp_back = self.board_size - 1 - self.index
        self.round_count = 0
        self.board = [[False for i in range(self.board_size)] for j in range(self.board_size)]
        self.prev_board = self.board
        self.attack_column = None

    def get_pos(self, r, c):
        # check space, except doesn't hit you with game errors
        if r < 0 or c < 0 or c >= board_size or r >= board_size:
            return False
        return check_space(r, c)
#        return self.board[r][c]

    def safe_spawn(self, i):
        if not inbounds(self.index, i):
            return False
        if self.get_pos(self.index + self.forward, i - 1) == opp_team or self.get_pos(self.index + self.forward, i + 1) == opp_team:
            return False
        if self.get_pos(self.index, i) in [team, opp_team]:
            return False
        spawn(self.index, i)
        return True

    def update_board(self):
        return
        board = []
        for r in range(self.board_size):
            row = []
            for c in range(self.board_size):
                row.append(check_space(r, c))
            board.append(row)
        self.prev_board = self.board
        self.board = board

    def get_row_count(self, row, t):
        count = 0
        for col in range(self.board_size):
            if self.get_pos(row, col) == t:
                count += 1
        return count

    def get_col_count(self, col, t):
        count = 0
        for row in range(self.board_size):
            if check_space(row, col) == t:
                count += 1
        return count
    
    def get_stalemate_line(self, col):
        for row in list(range(self.board_size))[::-1]:
            loc = map_loc(row)
            if self.get_pos(loc, col) == team:
                return loc
        return None

    def run(self):
        self.round_count = self.round_count + 1
        self.update_board()
        if self.defend():
            log("DEFENDED")
            return
        if self.round_count < 20:
            self.spawnheuristic(self.initial_heuristic)
        else:
            log("SPAWNING LOW")
#            if self.round_count % 50 < 15 or self.round_count > 480:
#            if self.round_count > GAME_MAX / 2:
            self.attack_column = None
            self.spawnheuristic(self.low_heuristic)
    
    def defend(self):
        if self.enemy_got_past():
            log("GOT PAST")
            return True
        if self.enemy_penetrated():
            log("PENETRATED")
            return True
        return False
    
    def enemy_got_past(self):
        cols = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                j = map_loc(j)
                if self.get_pos(j, i) == opp_team:
                    if self.safe_spawn(i):
                        return True
                elif self.get_pos(j, i) == team:
                    break
        return False

    def enemy_penetrated(self):
        cols = []
        for i in range(self.board_size):
            opp_locs = self.get_col_count(i, opp_team)
            my_locs = self.get_col_count(i, team)
            enemy_present = False
            for j in range(6):
                j = map_loc(j)
                if self.get_pos(j, i) == opp_team:
                    enemy_present = True
            if not enemy_present:
                continue
            cols.append((my_locs - opp_locs, my_locs, i))

        cols.sort()
        if len(cols) == 0:
            return False
        if cols[0][0] >= 0:
            return False
        for diff, my, i in cols:
            if not check_space(self.index, i):
                if self.safe_spawn(i):
                    return True
        return False

    def spawnheuristic(self, method, min=None, max=None):
        if min is None: min = 0
        if max is None: max = self.board_size
        # Spawns in the column w/ the lowest heuristic that's spawnable
        cols = [(method(i), i) for i in range(min, max)]
        cols.sort()
        for h, col in cols:
            if self.safe_spawn(col):
                return True
        return False        

    def initial_heuristic(self, col):
        allied = self.get_col_count(col, team)
        enemy = self.get_col_count(col, opp_team)
        if enemy > 0 and allied == 0:
            return -100 * enemy
        if enemy == 0 and allied == 0:
            if col != 0 and self.get_col_count(col - 1, opp_team) != 0:
                return 20
            if col != self.board_size - 1 and self.get_col_count(col + 1, opp_team) != 0:
                return 20
            return -20
        if allied > 0:
            return 100 * allied

    def low_heuristic(self, col):
        counts = []
        allied_count = self.get_col_count(col, team)
        enemy_count = self.get_col_count(col, opp_team)
        return allied_count * 100 - enemy_count * 50 + abs(col - 8)


robot = Pawn() if get_type() == RobotType.PAWN else Overlord()

def turn():
    """
    MUST be defined for robot to run
    This function will be called at the beginning of every turn and should contain the bulk of your robot commands
    """

    robot.run()
    if get_type() == RobotType.OVERLORD:
        bytecode = get_bytecode()
        log('Done! Bytecode left: ' + str(bytecode))
