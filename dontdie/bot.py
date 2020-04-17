import random


# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

DEBUG = 0
def dlog(str):
    if DEBUG > 0:
        log(str)


def check_space_wrapper(r, c, board_size):
    # check space, except doesn't hit you with game errors
    if r < 0 or c < 0 or c >= board_size or r >= board_size:
        return False
    try:
        return check_space(r, c)
    except:
        return None


team = get_team()
opp_team = Team.WHITE if team == Team.BLACK else team.BLACK
board_size = get_board_size()


class Pawn:
    def __init__(self):
        self.team = get_team()
        self.forward = 1 if self.team == Team.WHITE else -1
        self.type = "ATTACKER"
        self.board_size = get_board_size()

    def update_state(self):
        self.row, self.col = get_location()
        self.nextrow = self.row + self.forward

    def run(self):
        self.update_state()
        if self.type == "ATTACKER":
            self.runattacker()
        
        bytecode = get_bytecode()
        dlog('Done! Bytecode left: ' + str(bytecode))

    def runattacker(self):
        if self.trycapture():
            return
        if not self.forward_is_dangerous():
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

    def run(self):
        if self.team == Team.WHITE:
            index = 0
        else:
            index = self.board_size - 1

        for _ in range(self.board_size):
            i = random.randint(0, self.board_size - 1)
            if not check_space(index, i):
                spawn(index, i)
                dlog('Spawned unit at: (' + str(index) + ', ' + str(i) + ')')
                break


robot = Pawn() if get_type() == RobotType.PAWN else Overlord()

def turn():
    """
    MUST be defined for robot to run
    This function will be called at the beginning of every turn and should contain the bulk of your robot commands
    """

    robot.run()