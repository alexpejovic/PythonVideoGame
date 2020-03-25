import pytest
from typing import List, Tuple, Optional, Union
from block import Block
from blocky import _block_to_squares
from goal import BlobGoal, PerimeterGoal, _flatten, generate_goals, Goal
from player import _get_block
from renderer import Renderer
from settings import COLOUR_LIST
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PACIFIC_POINT = (1, 128, 181)
OLD_OLIVE = (138, 151, 71)
REAL_RED = (199, 44, 58)
MELON_MAMBO = (234, 62, 112)
DAFFODIL_DELIGHT = (255, 211, 92)
TEMPTING_TURQUOISE = (75, 196, 213)


def lone_block() -> Block:
    return Block((0, 0), 750, REAL_RED, 0, 0)

def set_children(block: Block, colours: List[Optional[Tuple[int, int, int]]]) \
        -> None:
    """Set the children at <level> for <block> using the given <colours>.

    Precondition:
        - len(colours) == 4
        - block.level + 1 <= block.max_depth
    """
    size = block._child_size()
    positions = block._children_positions()
    level = block.level + 1
    depth = block.max_depth

    block.children = []  # Potentially discard children
    for i in range(4):
        b = Block(positions[i], size, colours[i], level, depth)
        block.children.append(b)


def one_block_four_children() -> Block:
    b = Block((0, 0), 750, None, 0, 1)
    set_children(b, [TEMPTING_TURQUOISE, MELON_MAMBO, REAL_RED, OLD_OLIVE])
    return b


def one_block_sixteen_grandkids() -> Block:
    b = Block((0, 0), 750, None, 0, 2)
    set_children(b, [None, None, None, None])
    for child in b.children:
        set_children(child, [TEMPTING_TURQUOISE, MELON_MAMBO,
                             REAL_RED, OLD_OLIVE])
    return b


def one_block_4_children_8_grandkids_4_great_grandkids() -> Block:
    b = Block((0, 0), 750, None, 0, 3)
    set_children(b, [TEMPTING_TURQUOISE, DAFFODIL_DELIGHT, MELON_MAMBO,
                     OLD_OLIVE])
    for i in range(2):
        b.children[i].colour = None
        set_children(b.children[i], [TEMPTING_TURQUOISE, MELON_MAMBO,
                                     REAL_RED, TEMPTING_TURQUOISE])
    b.children[1].children[3].colour = None
    set_children(b.children[1].children[3], [OLD_OLIVE,
                                             OLD_OLIVE, REAL_RED,
                                             OLD_OLIVE])
    return b


def one_block_4_kids_one_kid_has_4_kids() -> Block:
    b = Block((0, 0), 750, None, 0, 2)
    set_children(b, [TEMPTING_TURQUOISE, MELON_MAMBO, REAL_RED, OLD_OLIVE])
    b.children[2].colour = None
    set_children(b.children[2], [TEMPTING_TURQUOISE, MELON_MAMBO,
                                 REAL_RED, REAL_RED])
    return b


def complicated_block_depth_3() -> Block:
    b = Block((0, 0), 750, None, 0, 3)
    set_children(b, [None, None, None, None])
    set_children(b.children[0], [TEMPTING_TURQUOISE, OLD_OLIVE,
                                 REAL_RED, MELON_MAMBO])
    set_children(b.children[1], [OLD_OLIVE, MELON_MAMBO,
                                 REAL_RED, None])
    set_children(b.children[1].children[3], [TEMPTING_TURQUOISE, MELON_MAMBO,
                                             MELON_MAMBO, REAL_RED])
    set_children(b.children[2], [OLD_OLIVE, TEMPTING_TURQUOISE, OLD_OLIVE, None])
    set_children(b.children[2].children[3], [REAL_RED, REAL_RED,
                                             TEMPTING_TURQUOISE,
                                             TEMPTING_TURQUOISE])
    set_children(b.children[3], [None, OLD_OLIVE, MELON_MAMBO,
                                 TEMPTING_TURQUOISE])
    set_children(b.children[3].children[0], [TEMPTING_TURQUOISE, REAL_RED,
                                             MELON_MAMBO, REAL_RED])
    return b


def complicated_block_depth_2() -> Block:
    b = Block((0, 0), 750, None, 0, 2)
    set_children(b, [REAL_RED, None, OLD_OLIVE, BLACK])
    set_children(b.children[1], [REAL_RED, OLD_OLIVE, MELON_MAMBO, BLACK])
    return b


def visited(board: Block) -> List[List[int]]:
    visits = []
    n = len(_flatten(board))
    for i in range(n):
        k = []
        for j in range(n):
            k.append(-1)
        visits.append(k)
    return visits




if __name__ == '__main__':
    pytest.main(['test_cases.py'])

