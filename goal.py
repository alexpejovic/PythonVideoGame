"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import math
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    pgoals = []
    bgoals = []
    for colour in COLOUR_LIST:
        pgoals.append(PerimeterGoal(colour))
        bgoals.append(BlobGoal(colour))

    r = random.randint(0, 1)
    if r == 0:
        goal_list = pgoals
    else:
        goal_list = bgoals

    goals = []
    for i in range(num_goals):
        r2 = random.randint(0, len(goal_list) - 1)
        goals.append(goal_list[r2])
        del goal_list[r2]

    return goals


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    if block.colour is not None:
        r = 2 ** (block.max_depth - block.level)
        lst = [[block.colour] * r] * r
        return lst
    else:
        up_right = _flatten(block.children[0])
        up_left = _flatten(block.children[1])
        down_left = _flatten(block.children[2])
        down_right = _flatten(block.children[3])
        lst = []
        for i in range(len(up_left)):
            lst.append(up_left[i] + down_left[i])

        for j in range(len(up_right)):
            lst.append(up_right[j] + down_right[j])

        return lst


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):

    def score(self, board: Block) -> int:

        flattened = _flatten(board)
        s = 0

        for i in range(1, len(flattened) - 1):
            if flattened[0][i] == self.colour:
                s += 1
            if flattened[-1][i] == self.colour:
                s += 1
            if flattened[i][0] == self.colour:
                s += 1
            if flattened[i][-1] == self.colour:
                s += 1

        if flattened[0][0] == self.colour:
            s += 2
        if flattened[0][-1] == self.colour:
            s += 2
        if flattened[-1][0] == self.colour:
            s += 2
        if flattened[-1][-1] == self.colour:
            s += 2

        return s

    def description(self) -> str:
        """ Returns a description describing the player's goal
        of getting as many unit blocks of colour <self.colour> on the
        perimeter of the game board.
        """
        c = colour_name(self.colour)
        return 'You must aim to put the most possible units of the' \
               ' colour' + c + ' on the outer perimeter of the board.' \
               ' Your score is the total number of unit cells of' \
            ' colour ' + c + ' that are on the perimeter. There is a premium' \
            ' on corner cells: they count twice towards the score.'


class BlobGoal(Goal):

    def score(self, board: Block) -> int:
        n = len(_flatten(board))
        visits = []
        for i in range(n):
            k = []
            for j in range(n):
                k.append(-1)
            visits.append(k)
        lst = []
        for i in range(len(_flatten(board))):
            for j in range(len(_flatten(board))):
                position = (i, j)
                lst.append(self._undiscovered_blob_size(position,
                                                        _flatten(board),
                                                        visits))
        return max(lst)

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        colour = self.colour
        i = pos[0]
        j = pos[1]
        not_on_board_i = i >= len(board) or i < 0
        not_on_board_j = j >= len(board) or j < 0
        if not_on_board_i or not_on_board_j:
            return 0
        elif visited[i][j] != -1:
            return 0
        elif board[i][j] != colour:
            visited[i][j] = 0
            return 0
        else:
            s = 1
            visited[i][j] = 1
            pos1 = (pos[0], pos[1] + 1)
            pos2 = (pos[0], pos[1] - 1)
            pos3 = (pos[0] + 1, pos[1])
            pos4 = (pos[0] - 1, pos[1])
            s += self._undiscovered_blob_size(pos1, board, visited)
            s += self._undiscovered_blob_size(pos2, board, visited)
            s += self._undiscovered_blob_size(pos3, board, visited)
            s += self._undiscovered_blob_size(pos4, board, visited)
            return s

    def description(self) -> str:
        """Returns a description of the player's goal, in which the player
        must create a connected set of blocks of a single colour
        """
        c = colour_name(self.colour)
        return 'You must aim for the largest “blob” of the colour' + c + '.' \
               ' A blob is a group of connected blocks with the same colour.' \
               ' Two blocks are connected if their sides touch; touching' \
               ' corners doesn’t count. Your score is the number of unit' \
               ' cells in the largest blob of colour ' + c + ' .'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })


