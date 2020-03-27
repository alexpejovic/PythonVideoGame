import pytest
from typing import List, Tuple, Optional, Union
from block import Block
from blocky import _block_to_squares
from goal import BlobGoal, PerimeterGoal, _flatten, generate_goals, Goal
from player import _get_block, create_players, Player, SmartPlayer, RandomPlayer, HumanPlayer
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


def test_perimeter_goal_score_lone_block() -> None:
    b = lone_block()
    goal = PerimeterGoal(REAL_RED)
    assert goal.score(b) == 4

def test_perimeter_goal_score_lone_block_max_depth_is_1() -> None:
    # max_depth = 1
    goal = PerimeterGoal(REAL_RED)
    block = lone_block()
    block.max_depth = 1
    assert goal.score(block) == 8


def test_blob_goal_score_lone_block() -> None:
    b = lone_block()
    # max_depth = 0
    goal = BlobGoal(REAL_RED)
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


# def test_generate_goals_length_of_list_returned() -> None:
#     assert len(generate_goals(1)) == 1
#     assert len(generate_goals(2)) == 2
#     assert len(generate_goals(3)) == 3
#     assert len(generate_goals(4)) == 4


# def test_generate_goals_type_of_goals_in_list_returned() -> None:
#     g1 = generate_goals(1)
#     g2 = generate_goals(2)
#     # g3 = generate_goals(3)
#     # g4 = generate_goals(4)
#
#     if not isinstance(g1[0], BlobGoal):
#         assert isinstance(g1[0], PerimeterGoal)
#     else:
#         assert isinstance(g1[0], BlobGoal)
#
#     for goal in g2:
#         if not isinstance(goal, BlobGoal):
#             assert isinstance(goal, PerimeterGoal)
#         else:
#             assert isinstance(goal, BlobGoal)

# def test_generate_goals_each_colour_goal_occurs_once() -> None:
#     g1 = generate_goals(1)
#     g2 = generate_goals(2)
#
#     colours_1 = []
#     for goal in g1:
#         colours_1.append(goal.colour)
#     for colour in colours_1:
#         assert colours_1.count(colour) == 1
#
#     colours_2 = []
#     for goal in g1:
#         colours_2.append(goal.colour)
#     for colour in colours_2:
#         assert colours_2.count(colour) == 1


def test_smash_1_block_4_kids_max_depth_is_1() -> None:
    b = one_block_four_children()
    b.max_depth = 1
    assert not b.smashable()
    for child in b.children:
        assert not child.smashable()


def test_smash_1_block_4_kids_max_depth_is_2() -> None:
    b = one_block_four_children()
    b.max_depth = 2
    for i in range(4):
        b.children[i].max_depth = 2
    assert not b.smashable()
    for child in b.children:
        assert child.smashable()

def test_smash_1_block_4_kids_one_kid_has_four_kids_depth_3() -> None:
    b = one_block_4_kids_one_kid_has_4_kids()
    b.max_depth = 3
    assert b.children[0].smashable()
    assert b.children[1].smashable()
    assert b.children[3].smashable()
    assert not b.children[2].smashable()

def test_smash_1_block_4_kids_one_kid_has_four_kids_depth_4() -> None:
    b = one_block_4_kids_one_kid_has_4_kids()
    b.max_depth = 4
    for i in range(4):
        b.children[i].max_depth = 4
    for i in range(4):
        b.children[2].children[i].max_depth = 4
    assert b.children[0].smashable()
    assert b.children[1].smashable()
    assert b.children[3].smashable()
    assert not b.children[2].smashable()
    assert b.children[2].children[0].smashable()
    assert b.children[2].children[1].smashable()
    assert b.children[2].children[2].smashable()
    assert b.children[2].children[3].smashable()

def test_get_block_when_block_is_at_level_0() -> None:
    # the block at level 0 is the deepest block
    # return that block

    b = lone_block()
    #location is in block
    assert _get_block(b, (0, 600), 3) == b
    assert _get_block(b, (0, 600), 0) == b

    #location is not in the block
    assert _get_block(b, (0, 760), 0) is None

    block_max_depth_is_5 = lone_block()
    block_max_depth_is_5.max_depth = 5
    assert _get_block(b, (0, 600), 3) == b

def test_get_block_one_block_4_kids_return_child_at_location() -> None:
    b = one_block_four_children()
    # position of child[0] is (375, 0)
    # position of child[1] is (0, 0)
    # position of child[2] is (0, 375)
    # position of child[3] is (375, 375)

    # location in child[0]
    location = (400, 40)
    assert _get_block(b, location, 1) == b.children[0]
    assert _get_block(b, location, 3) == b.children[0]
    assert _get_block(b, location, 0) == b

    # location in child[1]
    location = (3, 40)
    assert _get_block(b, location, 1) == b.children[1]
    assert _get_block(b, location, 3) == b.children[1]
    assert _get_block(b, location, 0) == b

    # location in child[2]
    location = (120, 450)
    assert _get_block(b, location, 1) == b.children[2]
    assert _get_block(b, location, 3) == b.children[2]
    assert _get_block(b, location, 0) == b

    # location in child[3]
    location = (600, 610)
    assert _get_block(b, location, 1) == b.children[3]
    assert _get_block(b, location, 3) == b.children[3]
    assert _get_block(b, location, 0) == b


def test_get_block_one_block_4_kids_one_kid_has_4_kids_returns_grandchild() -> None:
    b = one_block_4_kids_one_kid_has_4_kids()
    # position of child[0] is (375, 0)
    # position of child[1] is (0, 0)
    # position of child[2] is (0, 375)
    # position of child[3] is (375, 375)

    # position of child[2].child[0] is (188, 375)
    # position of child[2].child[1] is (0, 375)
    # position of child[2].child[2] is (0, 563)
    # position of child[2].child[3] is (188, 563)

    # edge cases
    location = (188, 600)
    assert _get_block(b, location, 1) == b.children[2]
    assert not _get_block(b, location, 2) == b.children[2].children[2]
    assert not _get_block(b, location, 2) == b.children[2].children[1]
    assert not _get_block(b, location, 2) == b.children[2].children[0]
    assert _get_block(b, location, 2) == b.children[2].children[3]
    location = (375, 500)
    assert not _get_block(b, location, 2) == b.children[2]
    assert _get_block(b, location, 2) == b.children[3]


    # location in child[0]
    location = (400, 40)
    assert _get_block(b, location, 1) == b.children[0]
    assert _get_block(b, location, 3) == b.children[0]
    assert _get_block(b, location, 0) == b

    # location in child[1]
    location = (3, 40)
    assert _get_block(b, location, 1) == b.children[1]
    assert _get_block(b, location, 3) == b.children[1]
    assert _get_block(b, location, 0) == b

    # location in child[2]
    location = (120, 450)
    assert _get_block(b, location, 1) == b.children[2]
    assert _get_block(b, location, 3) == b.children[2].children[1]
    assert _get_block(b, location, 0) == b

    location = (200, 700)
    assert _get_block(b, location, 1) == b.children[2]
    assert _get_block(b, location, 3) == b.children[2].children[3]
    assert _get_block(b, location, 0) == b

    location = (100, 700)
    assert _get_block(b, location, 1) == b.children[2]
    assert _get_block(b, location, 3) == b.children[2].children[2]
    assert _get_block(b, location, 0) == b

    location = (200, 400)
    assert _get_block(b, location, 1) == b.children[2]
    assert _get_block(b, location, 3) == b.children[2].children[0]
    assert _get_block(b, location, 0) == b

    # location in child[3]
    location = (600, 610)
    assert _get_block(b, location, 1) == b.children[3]
    assert _get_block(b, location, 3) == b.children[3]
    assert _get_block(b, location, 0) == b


def test_one_block_4_children_8_grandkids_4_great_grandkids() -> None:

    b = one_block_4_children_8_grandkids_4_great_grandkids()
    # position of child[0] is (375, 0)
    # position of child[1] is (0, 0)
    # position of child[2] is (0, 375)
    # position of child[3] is (375, 375)

    # position of child[0].child[0] is (563, 0)
    location = (600, 40)
    assert _get_block(b, location, 0) == b
    assert _get_block(b, location, 1) == b.children[0]
    assert _get_block(b, location, 2) == b.children[0].children[0]
    # position of child[0].child[1] is (375, 0)
    location = (500, 20)
    assert _get_block(b, location, 0) == b
    assert _get_block(b, location, 1) == b.children[0]
    assert _get_block(b, location, 2) == b.children[0].children[1]
    assert _get_block(b, location, 3) == b.children[0].children[1]
    # position of child[0].child[2] is (375, 188)
    location = (500, 200)
    assert _get_block(b, location, 0) == b
    assert _get_block(b, location, 1) == b.children[0]
    assert _get_block(b, location, 2) == b.children[0].children[2]
    assert _get_block(b, location, 3) == b.children[0].children[2]
    # position of child[0].child[3] is (563, 188)
    location = (600, 200)
    assert _get_block(b, location, 0) == b
    assert _get_block(b, location, 1) == b.children[0]
    assert _get_block(b, location, 2) == b.children[0].children[3]
    assert _get_block(b, location, 3) == b.children[0].children[3]

    # position of child[1].child[0] is (188, 0)
    location = (200, 20)
    assert _get_block(b, location, 0) == b
    assert _get_block(b, location, 1) == b.children[1]
    assert _get_block(b, location, 2) == b.children[1].children[0]
    assert _get_block(b, location, 3) == b.children[1].children[0]
    # position of child[1].child[1] is (0, 0)
    location = (100, 20)
    assert _get_block(b, location, 0) == b
    assert _get_block(b, location, 1) == b.children[1]
    assert _get_block(b, location, 2) == b.children[1].children[1]
    assert _get_block(b, location, 3) == b.children[1].children[1]
    # position of child[1].child[2] is (0, 188)
    location = (100, 200)
    assert _get_block(b, location, 0) == b
    assert _get_block(b, location, 1) == b.children[1]
    assert _get_block(b, location, 2) == b.children[1].children[2]
    assert _get_block(b, location, 3) == b.children[1].children[2]
    # position of child[1].child[3] is (188, 188)
    location = (200, 200)
    location1 = (300, 250)
    location2 = (200, 340)
    location3 = (330, 315)

    assert _get_block(b, location, 0) == b
    assert _get_block(b, location, 1) == b.children[1]
    assert _get_block(b, location, 2) == b.children[1].children[3]
    assert _get_block(b, location, 3) == b.children[1].children[3].children[1]

    assert _get_block(b, location1, 0) == b
    assert _get_block(b, location1, 1) == b.children[1]
    assert _get_block(b, location1, 2) == b.children[1].children[3]
    assert _get_block(b, location1, 3) == b.children[1].children[3].children[0]

    assert _get_block(b, location2, 0) == b
    assert _get_block(b, location2, 1) == b.children[1]
    assert _get_block(b, location2, 2) == b.children[1].children[3]
    assert _get_block(b, location2, 3) == b.children[1].children[3].children[2]

    assert _get_block(b, location3, 0) == b
    assert _get_block(b, location3, 1) == b.children[1]
    assert _get_block(b, location3, 2) == b.children[1].children[3]
    assert _get_block(b, location3, 3) == b.children[1].children[3].children[3]
    # position of child[1].child[3].child[0] is (282, 188)
    # position of child[1].child[3].child[1] is (188, 188)
    # position of child[1].child[3].child[2] is (188, 282)
    # position of child[1].child[3].child[3] is (282, 282)


def test_create_players_01_smart_players() -> None:
    assert create_players(0, 0, []) == []
    assert len(create_players(0, 0, [1])) == 1
    assert isinstance(create_players(0, 0, [1])[0], SmartPlayer)
    assert isinstance(create_players(0, 0, [4])[0], SmartPlayer)
    assert len(create_players(0, 0, [4])) == 1
    assert create_players(0, 0, [4])[0]._difficulty == 4
    assert create_players(0, 0, [1])[0]._difficulty == 1

def test_create_players_02_smart_players() -> None:
    created_players = create_players(0, 0, [1, 7, 5, 3])
    assert len(created_players) == 4
    for player in created_players:
        assert isinstance(player, SmartPlayer)
    created_players[0]._difficulty == 1
    created_players[1]._difficulty == 7
    created_players[2]._difficulty == 5
    created_players[3]._difficulty == 3

def test_create_players_03_human_player() -> None:
    created_players = create_players(1, 0, [])
    assert len(created_players) == 1
    assert isinstance(created_players[0], HumanPlayer)

    four_created_players = create_players(4, 0, [])
    assert len(four_created_players) == 4
    for player in four_created_players:
        assert isinstance(player, HumanPlayer)

def test_create_players_04_random_players() -> None:
    created_players = create_players(0, 7, [])
    assert len(created_players) == 7
    for player in created_players:
        assert isinstance(player, RandomPlayer)

def test_create_players_05_mixed_players() -> None:
    created_players = create_players(2, 3, [5, 6, 8])
    assert len(created_players) == 8
    for player in created_players[0:2]:
        assert isinstance(player, HumanPlayer)
    for player in created_players[2:5]:
        assert isinstance(player, RandomPlayer)
    for player in created_players[5:]:
        assert isinstance(player, SmartPlayer)

    assert created_players[5]._difficulty == 5
    assert created_players[6]._difficulty == 6
    assert created_players[7]._difficulty == 8

if __name__ == '__main__':
    pytest.main(['test_cases.py'])

