def get_candidates(board, row, col):
    if board[row][col] != 0:
        return set()
    
    candidates = set(range(1, 10))
    candidates -= set(board[row])
    candidates -= set(board[r][col] for r in range(9))

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            candidates.discard(board[r][c])

    return candidates


def find_naked_single(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                candidates = get_candidates(board, row, col)
                
                if len(candidates) == 1:
                    value = candidates.pop()
                    explanation = (
                        f"Look at row {row + 1}, column {col + 1}. "
                        f"Because of the other numbers in its row, column, and 3x3 box, "
                        f"the only possible number that can fit here is {value}."
                    )
                    return (row, col, value, explanation)
                    
    return None