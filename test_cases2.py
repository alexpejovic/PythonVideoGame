import pytest
from typing import List, Tuple, Optional, Union
from block import Block
from blocky import _block_to_squares
from goal import BlobGoal, PerimeterGoal, _flatten, generate_goals, Goal
from player import _is_move_valid, _get_block, create_players, Player, SmartPlayer, RandomPlayer, HumanPlayer
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

def lone_block() -> Block:
    return Block((0, 0), 750, REAL_RED, 0, 0)

def one_block_four_children_(max_depth: int) -> Block:
    b = Block((0, 0), 750, None, 0, max_depth)
    set_children(b, [TEMPTING_TURQUOISE, MELON_MAMBO, REAL_RED, OLD_OLIVE])
    return b


def one_block_sixteen_grandkids_(max_depth: int) -> Block:
    b = Block((0, 0), 750, None, 0, max_depth)
    set_children(b, [None, None, None, None])
    for child in b.children:
        set_children(child, [TEMPTING_TURQUOISE, MELON_MAMBO,
                             REAL_RED, OLD_OLIVE])
    return b


def one_block_4_children_8_grandkids_4_great_grandkids_(max_depth: int) -> Block:
    b = Block((0, 0), 750, None, 0, max_depth)
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


def one_block_4_kids_one_kid_has_4_kids_(max_depth: int) -> Block:
    b = Block((0, 0), 750, None, 0, max_depth)
    set_children(b, [TEMPTING_TURQUOISE, MELON_MAMBO, REAL_RED, OLD_OLIVE])
    b.children[2].colour = None
    set_children(b.children[2], [TEMPTING_TURQUOISE, MELON_MAMBO,
                                 REAL_RED, REAL_RED])
    return b


def complicated_block_depth_3_(max_depth: int) -> Block:
    b = Block((0, 0), 750, None, 0, max_depth)
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


def complicated_block_depth_2_(max_depth: int) -> Block:
    b = Block((0, 0), 750, None, 0, max_depth)
    set_children(b, [REAL_RED, None, OLD_OLIVE, BLACK])
    set_children(b.children[1], [REAL_RED, OLD_OLIVE, MELON_MAMBO, BLACK])
    return b


# TESTS FOR CREATE_COPY #
def test_create_copy_simple() -> None:
    b = lone_block()
    b_copy = b.create_copy()
    assert b == b_copy
    assert b is not b_copy
    b.colour = BLACK
    assert b != b_copy


def test_create_copy_cd2() -> None:
    b = complicated_block_depth_2_(2)
    b_copy = b.create_copy()
    assert b == b_copy
    assert b is not b_copy
    for i in range(4):
        assert b.children[i] == b_copy.children[i]
        assert b.children[i] is not b_copy.children[i]

    for i in range(4):
        assert b.children[1].children[i] == b_copy.children[1].children[i]
        assert b.children[1].children[i] is not b_copy.children[1].children[i]


# TESTS FOR ROTATE #
def test_rotate_lone() -> None:
    b = lone_block()
    assert not b.rotate(1)
    assert b == b


def test_rotate_logic() -> None:
    b = complicated_block_depth_3_(3)
    b2 = complicated_block_depth_3_(3)
    b.rotate(1)
    b2.rotate(3)
    b2.rotate(3)
    b2.rotate(3)
    assert b == b2


def test_non_rotation() -> None:
    b = one_block_4_kids_one_kid_has_4_kids_(5)
    assert not b.children[0].rotate(1)
    assert b.children[2].rotate(1)
    assert b.children[2].children[0].colour == MELON_MAMBO
    assert b.children[2].children[1].colour == REAL_RED
    assert b.children[2].children[2].colour == REAL_RED
    assert b.children[2].children[3].colour == TEMPTING_TURQUOISE


# TESTS FOR SWAP #
def test_swap_lone() -> None:
    b = lone_block()
    assert not b.swap(0)
    b2 = lone_block()
    assert b == b2
    assert b is not b2


def test_swap_logic() -> None:
    board = complicated_block_depth_3_(3)
    b = board.children[1].create_copy()
    b2 = board.children[1].create_copy()
    assert board.children[1].swap(0)
    assert b.swap(0)
    assert board.children[1] == b
    assert board.children[1].swap(0)
    assert board.children[1] == b2


def test_non_swap() -> None:
    board = one_block_4_kids_one_kid_has_4_kids_(2)
    board_copy = one_block_4_kids_one_kid_has_4_kids_(2)
    assert not board.children[1].swap(1)
    assert board == board_copy
    assert board.children[2].swap(1)
    assert board.children[2].children[0].colour == REAL_RED
    assert board.children[2].children[1].colour == REAL_RED
    assert board.children[2].children[2].colour == MELON_MAMBO
    assert board.children[2].children[3].colour == TEMPTING_TURQUOISE


# TESTS FOR PAINT #
def test_paint_lone() -> None:
    b = lone_block()
    assert not b.paint(REAL_RED)
    assert b.paint(TEMPTING_TURQUOISE)
    assert b.colour == TEMPTING_TURQUOISE


def test_paint_depth() -> None:
    board = one_block_four_children_(1)
    board2 = one_block_four_children_(2)
    assert board.children[0].paint(MELON_MAMBO)
    assert not board.children[1].paint(MELON_MAMBO)
    assert not board2.children[0].paint(MELON_MAMBO)
    assert not board2.children[1].paint(MELON_MAMBO)


def test_non_paint() -> None:
    board = one_block_sixteen_grandkids_(2)
    board_copy = one_block_sixteen_grandkids_(2)
    for i in range(4):
        assert not board.children[i].paint(REAL_RED)

    assert board == board_copy


# TESTS FOR COMBINE #
def test_combine_lone() -> None:
    b = lone_block()
    b2 = lone_block()
    assert not b.combine()
    assert b == b2


def test_combine_depth() -> None:
    board = one_block_4_children_8_grandkids_4_great_grandkids_(3)
    board2 = one_block_4_children_8_grandkids_4_great_grandkids_(4)
    assert board.children[1].children[3].colour is None
    assert board.children[1].children[3].combine()
    assert board.children[1].children[3].colour == OLD_OLIVE
    assert board2.children[1].children[3].colour is None
    assert not board2.children[1].children[3].combine()
    assert board2.children[1].children[3].colour is None


# TESTS FOR GENERATE MOVE #
def test_returns_block() -> None:
    """This one fails a lot because block.combine() is buggy because we are
    using colours that are not in COLOUR_LIST, something which they do not
    test for.
    """
    gr = BlobGoal(REAL_RED)
    gp = PerimeterGoal(MELON_MAMBO)
    board = one_block_four_children_(1)
    rp = RandomPlayer(0, gr)
    sp = SmartPlayer(1, gp, 10)
    rp._proceed = True
    sp._proceed = True
    move_block_rp = rp.generate_move(board)[2]
    move_block_sp = sp.generate_move(board)[2]
    assert move_block_rp == board or move_block_rp in board.children
    assert move_block_sp == board or move_block_sp in board.children


def test_score_is_greater() -> None:
    """Same shit w last method"""
    gp = PerimeterGoal(MELON_MAMBO)
    board = one_block_four_children_(1)
    sp = SmartPlayer(1, gp, 4)
    sp._proceed = True
    move = sp.generate_move(board)
    score = gp.score(board)
    if move[0] != 'pass':
        assert _is_move_valid(sp, move[2], (move[0], move[1]))
    score2 = gp.score(board)
    if move[0] != 'pass':
        assert score2 > score
    else:
        assert score2 == score





if __name__ == '__main__':
    pytest.main(['test_cases2.py'])
