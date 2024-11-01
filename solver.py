import itertools

import numpy as np
import pandas as pd


def create_board(file_path) -> np.ndarray:
    """Create a numpy array from a csv file for the sudoku board."""
    return pd.read_csv(file_path, header=None, index_col=False).to_numpy()


def create_unknowns_dict(board: np.ndarray) -> dict:
    """Create a dictionary of possible values for empty cells in the sudoku board."""
    return {
        (i, j): [str(x) for x in range(1, 10)]
        for i in range(9)
        for j in range(9)
        if board[i][j] == "X"
    }


def get_row(board: np.ndarray, X: int) -> list[int]:
    """Get the values of a row in the sudoku board."""
    return [x for x in board[X] if x != "X"]


def get_column(board: np.ndarray, Y: int) -> list[int]:
    """Get the values of a column in the sudoku board."""
    return [x for x in board[:, Y] if x != "X"]


def get_square(board: np.ndarray, X: int, Y: int) -> list[int]:
    """Get the values of a square in the sudoku board."""
    return [
        board[i][j]
        for i in range(X // 3 * 3, X // 3 * 3 + 3)
        for j in range(Y // 3 * 3, Y // 3 * 3 + 3)
        if board[i][j] != "X"
    ]


def remove_impossible_values(
    X: int, Y: int, possible: list[int], board: np.ndarray
) -> list[int]:
    """Remove values that are not possible for a cell in the sudoku board."""
    impossible_values = set(
        get_row(board, X) + get_column(board, Y) + get_square(board, X, Y)
    )
    return [x for x in possible if x not in impossible_values]


def check_only_possible_location(
    key: tuple[int, int], value: int, unknowns: dict
) -> bool:
    """Check if a cell is the only possible location for a value."""
    row = [x[1] for x in unknowns.items() if x[0][0] == key[0] and x[0] != key]
    column = [x[1] for x in unknowns.items() if x[0][1] == key[1] and x[0] != key]
    square = [
        unknowns.get((key[0] // 3 * 3 + i, key[1] // 3 * 3 + j), [])
        for i in range(3)
        for j in range(3)
        if (key[0] // 3 * 3 + i, key[1] // 3 * 3 + j) != key
    ]
    flattened_row = set(itertools.chain(*row))
    flattened_column = set(itertools.chain(*column))
    flattened_square = set(itertools.chain(*square))
    return (
        value not in flattened_row
        or value not in flattened_column
        or value not in flattened_square
    )


def solve_board(file_path: str) -> np.ndarray:
    """Solve a sudoku board."""
    board = create_board(file_path)
    unknowns = create_unknowns_dict(board)
    iterations = 0

    while "X" in board:
        start_board = board.copy()
        for key in unknowns:
            unknowns[key] = remove_impossible_values(
                key[0], key[1], unknowns[key], board
            )
            if len(unknowns[key]) == 1:
                board[key[0]][key[1]] = unknowns[key][0]

        for key in unknowns:
            for value in unknowns[key]:
                if check_only_possible_location(key, value, unknowns):
                    board[key] = value
                    unknowns[key] = [value]
                    break

        iterations += 1
        if np.array_equal(start_board, board):
            break

    try:
        check_solution(board)
        print(f"SOLVED! (in {iterations} iterations)")
    except AssertionError:
        print(f"NOT SOLVED! (in {iterations} iterations)")
    return board


def check_solution(board: np.ndarray):
    """Check if a sudoku board is solved."""
    for row in board:
        assert len(set(row)) == 9
    for column in board.T:
        assert len(set(column)) == 9
    for i in range(3):
        for j in range(3):
            assert len(set(board[i * 3 : i * 3 + 3, j * 3 : j * 3 + 3].flatten())) == 9
    assert np.all(board != "X")
    board = board.astype(int)
    assert np.all(board <= 9) and np.all(board >= 1)
    assert np.sum(board) == 405


def pretty_print_board(board: np.ndarray):
    """Print a sudoku board in a pretty format."""
    for count, row in enumerate(board):
        if count % 3 == 0 and count != 0:
            print("------+-------+------")
        print(
            " ".join(
                [str(x) for x in row[:3]]
                + ["|"]
                + [str(x) for x in row[3:6]]
                + ["|"]
                + [str(x) for x in row[6:9]]
            )
        )
