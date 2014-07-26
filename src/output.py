"""Imago output module."""

import copy
import sys

COORDS = 'abcdefghijklmnopqrs'

# TODO refactor method names

class Board:
    """Represents the state of the board."""
    def __init__(self, size, stones):
        self.stones = stones        
        self.size = size

    def __str__(self):
        """Retrun string representation of the board."""
        lines = []
        k = 0
        for i in range(self.size):
            line = []
            for j in range(self.size):
                line.append(self.stones[k])
                k += 1
            lines.append(" ".join(line))
        lines.append("")
        return ("\n".join(lines))

    def asSGFsetPos(self):
        """Returns SGF (set position) representation of the position."""

        #TODO version numbering
        sgf = "(;FF[4]GM[1]SZ[" + str(self.size) + "]AP[Imago:0.1.0]\n"
        sgf += self.SGFpos()
        sgf += ")"
        return sgf

    def SGFpos(self):
        black = []
        white = []

        for i in range(self.size):
            for j in range(self.size):
                stone = self.stones[i * self.size + j]
                if stone == 'B':
                    black.append(Move('B', i, j))
                elif stone == 'W':
                    white.append(Move('W', i, j))
        sgf = ""
        if len(black) > 0:
            sgf += "AB" + ''.join('[' + m.sgf_coords() + ']'
                              for m in black) + "\n"
        if len(white) > 0:
            sgf += "AW" + ''.join('[' + m.sgf_coords() + ']' 
                              for m in white) + "\n"
        return sgf

    def addMove(self, m):
        """Add move to the board."""
        self.stones[(m.y * self.size) + m.x] = m.color

    def getMoveCandidates(self, board):
        """Take the next board in game and return a list of moves that are
        new."""
        candidates = []
        for i in range(self.size):
            for j in range(self.size):
                if (self.stones[self.size * i + j] == "."):
                    if (board.stones[self.size * i + j] == "W"):
                        candidates.append(Move("W", i, j))
                    elif (board.stones[self.size * i + j] == "B"):
                        candidates.append(Move("B", i, j))
        return candidates

class Move:
    """Repsresents a move."""
    def __init__(self, color, y, x, comment=None):
        self.color = color
        self.x = x
        self.y = y
        self.comment = comment

    def sgf_coords(self):
        """Return coordinates of the move in SGF."""
        return COORDS[self.x] + COORDS[self.y]

class Game:
    """Represents a game."""
    def __init__(self, size, board=None, debug=True):
        self.init_board = board or Board(size, (size * size) * ".")
        self.board = copy.deepcopy(self.init_board)
        self.moves = []
        self.size = size
        self.debug = debug
        self.debug_comment = ""

    def addMove(self, board):
        """Add next move to the game."""
        candidates = self.board.getMoveCandidates(board)
        if self.debug:
            comment = str(board)
            comment += "Candidates: " + str(len(candidates))
            
        if not candidates:
            self.debug_comment += "No candidates."
            return

        move = candidates[0]
        move.comment = comment
        self.moves.append(move)
        self.board.addMove(move)

    def asSGF(self):
        """Return the game representation as SGF string."""
        sgf = "(;FF[4]GM[1]SZ[" + str(self.size) + "]AP[Imago:0.1.0]\n"
        sgf += self.init_board.SGFpos()
        for m in self.moves:
            if m:
                sgf += ";" + m.color + "[" + m.sgf_coords() + "]"
                if m.comment:
                    sgf += "C[" + m.comment + "]"
                sgf += "\n"
        sgf += ")"
        return sgf


