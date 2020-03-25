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




# === TESTS ===

def test_block_to_squares_lone_block() -> None:
    b = lone_block()
    assert _block_to_squares(b) == [(REAL_RED, (0,0), 750)]

def test_block_to_squares_one_block_four_children() -> None:
    b = one_block_four_children()
    assert _block_to_squares(b) == [(TEMPTING_TURQUOISE, b.children[0].position,
                                     b.children[0].size),
                                    (MELON_MAMBO, b.children[1].position,
                                     b.children[1].size),
                                    (REAL_RED, b.children[2].position,
                                     b.children[2].size),
                                    (OLD_OLIVE, b.children[3].position,
                                     b.children[3].size)]

def test_block_to_squares_one_block_16_grandkids() -> None:
    b = one_block_sixteen_grandkids()
    assert _block_to_squares(b) == [(TEMPTING_TURQUOISE,
                                     b.children[0].children[0].position,
                                     b.children[0].children[0].size),
                                    (MELON_MAMBO,
                                     b.children[0].children[1].position,
                                     b.children[0].children[1].size),
                                    (REAL_RED,
                                     b.children[0].children[2].position,
                                     b.children[0].children[2].size),
                                    (OLD_OLIVE,
                                     b.children[0].children[3].position,
                                     b.children[0].children[3].size),
                                    (TEMPTING_TURQUOISE,
                                     b.children[1].children[0].position,
                                     b.children[1].children[0].size),
                                    (MELON_MAMBO,
                                     b.children[1].children[1].position,
                                     b.children[1].children[1].size),
                                    (REAL_RED,
                                     b.children[1].children[2].position,
                                     b.children[1].children[2].size),
                                    (OLD_OLIVE,
                                     b.children[1].children[3].position,
                                     b.children[1].children[3].size),
                                    (TEMPTING_TURQUOISE,
                                     b.children[2].children[0].position,
                                     b.children[2].children[0].size),
                                    (MELON_MAMBO,
                                     b.children[2].children[1].position,
                                     b.children[2].children[1].size),
                                    (REAL_RED,
                                     b.children[2].children[2].position,
                                     b.children[2].children[2].size),
                                    (OLD_OLIVE,
                                     b.children[2].children[3].position,
                                     b.children[2].children[3].size),
                                    (TEMPTING_TURQUOISE,
                                     b.children[3].children[0].position,
                                     b.children[3].children[0].size),
                                    (MELON_MAMBO,
                                     b.children[3].children[1].position,
                                     b.children[3].children[1].size),
                                    (REAL_RED,
                                     b.children[3].children[2].position,
                                     b.children[3].children[2].size),
                                    (OLD_OLIVE,
                                     b.children[3].children[3].position,
                                     b.children[3].children[3].size)]

def test_block_to_squares_one_block_4_children_8_grandkids_4_great_grandkids() -> None:
    b = one_block_4_children_8_grandkids_4_great_grandkids()
    assert _block_to_squares(b) == \
           [(TEMPTING_TURQUOISE, b.children[0].children[0].position, b.children[0].children[0].size),
            (MELON_MAMBO, b.children[0].children[1].position, b.children[0].children[1].size),
            (REAL_RED, b.children[0].children[2].position, b.children[0].children[2].size),
            (TEMPTING_TURQUOISE, b.children[0].children[3].position, b.children[0].children[3].size),
            (TEMPTING_TURQUOISE, b.children[1].children[0].position, b.children[1].children[0].size),
            (MELON_MAMBO, b.children[1].children[1].position, b.children[1].children[1].size),
            (REAL_RED, b.children[1].children[2].position, b.children[1].children[2].size),
            (OLD_OLIVE, b.children[1].children[3].children[0].position, b.children[1].children[3].children[0].size),
            (OLD_OLIVE, b.children[1].children[3].children[1].position, b.children[1].children[3].children[1].size),
            (REAL_RED, b.children[1].children[3].children[2].position, b.children[1].children[3].children[2].size),
            (OLD_OLIVE, b.children[1].children[3].children[3].position, b.children[1].children[3].children[3].size),
            (MELON_MAMBO, b.children[2].position, b.children[2].size), (OLD_OLIVE, b.children[3].position, b.children[3].size)]


def test_block_to_squares_one_block_4_kids_one_kid_has_four_kids() -> None:
    b = one_block_4_kids_one_kid_has_4_kids()
    assert _block_to_squares(b) == \
           [(TEMPTING_TURQUOISE, b.children[0].position, b.children[0].size),
            (MELON_MAMBO, b.children[1].position, b.children[1].size),
            (TEMPTING_TURQUOISE, b.children[2].children[0].position, b.children[2].children[0].size),
            (MELON_MAMBO, b.children[2].children[1].position, b.children[2].children[1].size),
            (REAL_RED, b.children[2].children[2].position, b.children[2].children[2].size),
            (REAL_RED, b.children[2].children[3].position, b.children[2].children[3].size),
            (OLD_OLIVE, b.children[3].position, b.children[3].size)]


def test_smash_lone_block_01() -> None:
    # max_level is 0
    b = Block((0, 0), 750, REAL_RED, 0, 0)
    assert not b.smash()


def test_smash_lone_block_02() -> None:
    # max_level is 1
    b = Block((0, 0), 750, OLD_OLIVE, 0, 1)
    assert b.smash()


def test_flatten_complicated_block_depth_2() -> None:
    b = complicated_block_depth_2()
    assert _flatten(b) == [[(OLD_OLIVE), (MELON_MAMBO), (OLD_OLIVE), (OLD_OLIVE)],
                           [(REAL_RED), (BLACK), (OLD_OLIVE), (OLD_OLIVE)],
                           [(REAL_RED), (REAL_RED), (BLACK), (BLACK)],
                           [(REAL_RED), (REAL_RED), (BLACK), (BLACK)]]

def test_flatten_complicated_block_depth_3() -> None:
    b =  complicated_block_depth_3()
    assert _flatten(b) == \
           [[(MELON_MAMBO), (MELON_MAMBO), (REAL_RED), (REAL_RED),
             (TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE), (OLD_OLIVE), (OLD_OLIVE)],
            [(MELON_MAMBO), (MELON_MAMBO), (REAL_RED), (REAL_RED),
             (TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE), (OLD_OLIVE), (OLD_OLIVE)],
            [(OLD_OLIVE), (OLD_OLIVE), (MELON_MAMBO), (MELON_MAMBO),
             (OLD_OLIVE), (OLD_OLIVE), (REAL_RED), (TEMPTING_TURQUOISE)],
            [(OLD_OLIVE), (OLD_OLIVE), (TEMPTING_TURQUOISE), (REAL_RED),
             (OLD_OLIVE), (OLD_OLIVE), (REAL_RED), (TEMPTING_TURQUOISE)],
            [(OLD_OLIVE), (OLD_OLIVE), (REAL_RED), (REAL_RED),
             (OLD_OLIVE), (OLD_OLIVE), (MELON_MAMBO), (MELON_MAMBO)],
            [(OLD_OLIVE), (OLD_OLIVE), (REAL_RED), (REAL_RED),
             (OLD_OLIVE), (OLD_OLIVE), (MELON_MAMBO), (MELON_MAMBO)],
            [(TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE), (MELON_MAMBO), (MELON_MAMBO),
             (REAL_RED), (MELON_MAMBO), (TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE)],
            [(TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE), (MELON_MAMBO), (MELON_MAMBO),
             (TEMPTING_TURQUOISE), (REAL_RED), (TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE)]]


def test_flatten_lone_block() -> None:
    b = lone_block()
    assert _flatten(b) == [[(REAL_RED)]]


def test_flatten_one_block_four_children() -> None:
    b = one_block_four_children()
    assert _flatten(b) == [[(MELON_MAMBO), (REAL_RED)],
                           [(TEMPTING_TURQUOISE), (OLD_OLIVE)]]

def test_flatten_one_block_16_grandkids() -> None:
    b = one_block_sixteen_grandkids()
    assert _flatten(b) == \
           [[(MELON_MAMBO), (REAL_RED), (MELON_MAMBO), (REAL_RED)],
            [(TEMPTING_TURQUOISE), (OLD_OLIVE), (TEMPTING_TURQUOISE), (OLD_OLIVE)],
            [(MELON_MAMBO), (REAL_RED), (MELON_MAMBO), (REAL_RED)],
            [(TEMPTING_TURQUOISE), (OLD_OLIVE), (TEMPTING_TURQUOISE), (OLD_OLIVE)]]

def test_flatten_one_block_4_children_8_grandkids_4_great_grandkids() -> None:
    b = one_block_4_children_8_grandkids_4_great_grandkids()
    assert _flatten(b) == \
           [[(MELON_MAMBO), (MELON_MAMBO), (REAL_RED), (REAL_RED), (MELON_MAMBO),
             (MELON_MAMBO), (MELON_MAMBO), (MELON_MAMBO)],
            [(MELON_MAMBO), (MELON_MAMBO), (REAL_RED), (REAL_RED), (MELON_MAMBO),
             (MELON_MAMBO), (MELON_MAMBO), (MELON_MAMBO)],
            [(TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE), (OLD_OLIVE), (REAL_RED),
             (MELON_MAMBO), (MELON_MAMBO), (MELON_MAMBO), (MELON_MAMBO)],
            [(TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE), (OLD_OLIVE), (OLD_OLIVE),
             (MELON_MAMBO), (MELON_MAMBO), (MELON_MAMBO), (MELON_MAMBO)],
            [(MELON_MAMBO), (MELON_MAMBO), (REAL_RED), (REAL_RED),
             (OLD_OLIVE), (OLD_OLIVE), (OLD_OLIVE), (OLD_OLIVE)],
            [(MELON_MAMBO), (MELON_MAMBO), (REAL_RED), (REAL_RED),
             (OLD_OLIVE), (OLD_OLIVE), (OLD_OLIVE), (OLD_OLIVE)],
            [(TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE),
             (TEMPTING_TURQUOISE),(OLD_OLIVE), (OLD_OLIVE), (OLD_OLIVE),
             (OLD_OLIVE)],
            [(TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE),
             (TEMPTING_TURQUOISE),(OLD_OLIVE), (OLD_OLIVE), (OLD_OLIVE),
             (OLD_OLIVE)]]


def test_flatten_one_block_4_kids_one_kid_has_4_kids() -> None:
    b = one_block_4_kids_one_kid_has_4_kids()
    assert _flatten(b) == \
           [[(MELON_MAMBO), (MELON_MAMBO), (MELON_MAMBO), (REAL_RED)],
            [(MELON_MAMBO), (MELON_MAMBO), (TEMPTING_TURQUOISE), (REAL_RED)],
            [(TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE), (OLD_OLIVE), (OLD_OLIVE)],
            [(TEMPTING_TURQUOISE), (TEMPTING_TURQUOISE), (OLD_OLIVE), (OLD_OLIVE)]]


def test_perimeter_score_goal_complicated_block_depth_2() -> None:
    b = complicated_block_depth_2()

    # perimeter score for red colour
    goal = PerimeterGoal(REAL_RED)
    assert goal.score(b) == 5

    # perimeter score for black colour
    goal = PerimeterGoal(BLACK)
    assert goal.score(b) == 4

    # perimeter score for green colour
    goal = PerimeterGoal(OLD_OLIVE)
    assert goal.score(b) == 6

    # perimeter score for yellow colour
    goal = PerimeterGoal(MELON_MAMBO)
    assert goal.score(b) == 1

def test_perimeter_goal_score_complicated_block_depth_3() -> None:
    b = complicated_block_depth_3()

    # perimeter score for red colour
    goal = PerimeterGoal(REAL_RED)
    assert goal.score(b) == 3

    # perimeter score for blue colour
    goal = PerimeterGoal(TEMPTING_TURQUOISE)
    assert goal.score(b) == 13

    # perimeter score for green colour
    goal = PerimeterGoal(OLD_OLIVE)
    assert goal.score(b) == 8

    # perimeter score for yellow colour
    goal = PerimeterGoal(MELON_MAMBO)
    assert goal.score(b) == 8


def test_BlobGoal_undiscovered_blob_size_complicated_block_depth_2_red() -> None:
    b = complicated_block_depth_2()

    # The goals colour is red
    goal = BlobGoal(REAL_RED)

    assert goal._undiscovered_blob_size((1, 0), _flatten(b), visited(b)) == 5
    assert goal._undiscovered_blob_size((2, 0), _flatten(b), visited(b)) == 5
    assert goal._undiscovered_blob_size((3, 0), _flatten(b), visited(b)) == 5
    assert goal._undiscovered_blob_size((2, 1), _flatten(b), visited(b)) == 5
    assert goal._undiscovered_blob_size((3, 1), _flatten(b), visited(b)) == 5

    # doesn't include the colour
    assert goal._undiscovered_blob_size((1, 1), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((0, 3), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((0, 2), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((2, 2), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((3, 2), _flatten(b), visited(b)) == 0

    # coordinated are out of bounds
    assert goal._undiscovered_blob_size((5, 7), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((4, 1), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((1, 4), _flatten(b), visited(b)) == 0


def test_BlobGoal_undiscovered_blob_size_complicated_block_depth_2_black() -> None:
    b = complicated_block_depth_2()

    # The goals colour is black
    goal = BlobGoal(BLACK)

    # coordinate includes colour black
    assert goal._undiscovered_blob_size((2, 2), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((2, 3), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((3, 2), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((3, 3), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((1, 1), _flatten(b), visited(b)) == 1

    # coordinate doesn't include the colour black
    assert goal._undiscovered_blob_size((1, 0), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((1, 3), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((3, 0), _flatten(b), visited(b)) == 0


def test_BlobGoal_undiscovered_blob_size_complicated_block_depth_2_green() -> None:
    b = complicated_block_depth_2()

    # The goals colour is green
    goal = BlobGoal(OLD_OLIVE)

    # coordinate includes colour green
    assert goal._undiscovered_blob_size((0, 2), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((0, 3), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((1, 2), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((1, 3), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((0, 0), _flatten(b), visited(b)) == 1

    # coordinate doesn't include the colour green
    assert goal._undiscovered_blob_size((1, 0), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((3, 3), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((3, 0), _flatten(b), visited(b)) == 0


def test_BlobGoal_undiscovered_blob_size_complicated_block_depth_2_yellow() -> None:
    b = complicated_block_depth_2()

    # The goals colour is yellow
    goal = BlobGoal(MELON_MAMBO)

    # coordinate includes colour yellow
    assert goal._undiscovered_blob_size((0, 1), _flatten(b), visited(b)) == 1

    # coordinate doesn't include the colour yellow
    assert goal._undiscovered_blob_size((1, 0), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((3, 3), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((2, 2), _flatten(b), visited(b)) == 0


def test_BlobGoal_undiscovered_blob_size_complicated_block_depth_3_yellow() -> None:

    b = complicated_block_depth_3()
    # the goal of this colour is yellow
    goal = BlobGoal(MELON_MAMBO)

    # coordinate includes the colour yellow
    assert goal._undiscovered_blob_size((1, 0), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((0, 1), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((0, 0), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((1, 1), _flatten(b), visited(b)) == 4

    assert goal._undiscovered_blob_size((2, 2), _flatten(b), visited(b)) == 2
    assert goal._undiscovered_blob_size((2, 3), _flatten(b), visited(b)) == 2

    assert goal._undiscovered_blob_size((6, 5), _flatten(b), visited(b)) == 1

    # coordinate doesn't include colour yellow
    assert goal._undiscovered_blob_size((4, 0), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((0, 4), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((5, 3), _flatten(b), visited(b)) == 0


def test_BlobGoal_undiscovered_blob_size_complicated_block_depth_3_green() -> None:

    b = complicated_block_depth_3()

    # the goal of this colour is green
    goal = BlobGoal(OLD_OLIVE)

    # coordinate includes the colour green
    assert goal._undiscovered_blob_size((2, 0), _flatten(b), visited(b)) == 8
    assert goal._undiscovered_blob_size((2, 1), _flatten(b), visited(b)) == 8
    assert goal._undiscovered_blob_size((5, 5), _flatten(b), visited(b)) == 8
    assert goal._undiscovered_blob_size((5, 1), _flatten(b), visited(b)) == 8
    assert goal._undiscovered_blob_size((2, 4), _flatten(b), visited(b)) == 8

    assert goal._undiscovered_blob_size((0, 7), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((0, 6), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((1, 7), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((1, 6), _flatten(b), visited(b)) == 4

    # coordinate doesn't include colour green
    assert goal._undiscovered_blob_size((1, 0), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((6, 0), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((3, 2), _flatten(b), visited(b)) == 0

    # coordinate out of bounds
    assert goal._undiscovered_blob_size((8, 1), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((2, 9), _flatten(b), visited(b)) == 0

def test_BlobGoal_undiscovered_blob_size_complicated_block_depth_3_blue() -> None:
    b = complicated_block_depth_3()

    # the goal of this colour is blue
    goal = BlobGoal(TEMPTING_TURQUOISE)

    # coordinate includes the colour blue
    assert goal._undiscovered_blob_size((7, 0), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((7, 7), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((6, 0), _flatten(b), visited(b)) == 4

    assert goal._undiscovered_blob_size((7, 4), _flatten(b), visited(b)) == 1
    assert goal._undiscovered_blob_size((3, 2), _flatten(b), visited(b)) == 1

    assert goal._undiscovered_blob_size((2, 7), _flatten(b), visited(b)) == 2
    assert goal._undiscovered_blob_size((3, 7), _flatten(b), visited(b)) == 2

    # coordinate doesn't include colour blue
    assert goal._undiscovered_blob_size((1, 0), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((3, 3), _flatten(b), visited(b)) == 0

    # coordinate out of bounds
    assert goal._undiscovered_blob_size((8, 1), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((2, 9), _flatten(b), visited(b)) == 0


def test_BlobGoal_undiscovered_blob_size_complicated_block_depth_3_red() -> None:
    b = complicated_block_depth_3()

    # the goal of this colour is red
    goal = BlobGoal(REAL_RED)

    # coordinate includes the colour red
    assert goal._undiscovered_blob_size((0, 2), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((1, 3), _flatten(b), visited(b)) == 4
    assert goal._undiscovered_blob_size((0, 3), _flatten(b), visited(b)) == 4

    assert goal._undiscovered_blob_size((2, 6), _flatten(b), visited(b)) == 2
    assert goal._undiscovered_blob_size((3, 6), _flatten(b), visited(b)) == 2

    assert goal._undiscovered_blob_size((7, 5), _flatten(b), visited(b)) == 1
    assert goal._undiscovered_blob_size((6, 4), _flatten(b), visited(b)) == 1

    assert goal._undiscovered_blob_size((3, 3), _flatten(b), visited(b)) == 5

    # coordinate doesn't include colour red
    assert goal._undiscovered_blob_size((0, 7), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((2, 7), _flatten(b), visited(b)) == 0

    # coordinate out of bounds
    assert goal._undiscovered_blob_size((8, 1), _flatten(b), visited(b)) == 0
    assert goal._undiscovered_blob_size((2, 9), _flatten(b), visited(b)) == 0

def test_BlobGoal_score_complicated_depth_3_red() -> None:
    b = complicated_block_depth_3()
    # the goal of this colour is red
    goal = BlobGoal(REAL_RED)

    assert goal.score(b) == 5

def test_BlobGoal_score_complicated_depth_3_blue() -> None:
    b = complicated_block_depth_3()
    # the goal of this colour is blue
    goal = BlobGoal(TEMPTING_TURQUOISE)

    assert goal.score(b) == 4

def test_BlobGoal_score_complicated_depth_3_green() -> None:
    b = complicated_block_depth_3()

    # the goal of this colour is green
    goal = BlobGoal(OLD_OLIVE)

    assert goal.score(b) == 8

def test_BlobGoal_score_complicated_depth_3_yellow() -> None:
    b = complicated_block_depth_3()

    # the goal of this colour is yellow
    goal = BlobGoal(MELON_MAMBO)

    assert goal.score(b) == 4

def test_BlobGoal_score_complicated_depth_2_red() -> None:
    b = complicated_block_depth_2()
    # the goal of this colour is red
    goal = BlobGoal(REAL_RED)

    assert goal.score(b) == 5

def test_BlobGoal_score_complicated_depth_2_blacl() -> None:
    b = complicated_block_depth_2()
    # the goal of this colour is black
    goal = BlobGoal(BLACK)

    assert goal.score(b) == 4

def test_BlobGoal_score_complicated_depth_2_green() -> None:
    b = complicated_block_depth_2()
    # the goal of this colour is green
    goal = BlobGoal(OLD_OLIVE)

    assert goal.score(b) == 4


def test_BlobGoal_score_complicated_depth_2_yellow() -> None:
    b = complicated_block_depth_2()
    # the goal of this colour is yellow
    goal = BlobGoal(MELON_MAMBO)

    assert goal.score(b) == 1


if __name__ == '__main__':
    pytest.main(['test_cases.py'])

