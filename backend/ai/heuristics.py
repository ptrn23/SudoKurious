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

def find_hidden_single(board):
    # check rows
    for row in range(9):
        for value in range(1, 10):
            possible_cols = []
            for col in range(9):
                if board[row][col] == 0 and value in get_candidates(board, row, col):
                    possible_cols.append(col)
                    
            if len(possible_cols) == 1:
                col = possible_cols[0]
                explanation = (
                    f"Look at row {row + 1}. "
                    f"The number {value} can only be placed in column {col + 1} "
                    f"because all other empty cells in this row are blocked by a {value} in their intersecting column or box."
                )
                return (row, col, value, explanation)

    # check columns
    for col in range(9):
        for value in range(1, 10):
            possible_rows = []
            for row in range(9):
                if board[row][col] == 0 and value in get_candidates(board, row, col):
                    possible_rows.append(row)
                    
            if len(possible_rows) == 1:
                row = possible_rows[0]
                explanation = (
                    f"Look at column {col + 1}. "
                    f"The number {value} can only be placed in row {row + 1} "
                    f"because all other empty cells in this column are blocked."
                )
                return (row, col, value, explanation)

    # check 3x3 boxes
    for box_row in range(3):
        for box_col in range(3):
            for value in range(1, 10):
                possible_cells = []
                start_row, start_col = box_row * 3, box_col * 3
                
                for r in range(start_row, start_row + 3):
                    for c in range(start_col, start_col + 3):
                        if board[r][c] == 0 and value in get_candidates(board, r, c):
                            possible_cells.append((r, c))
                            
                if len(possible_cells) == 1:
                    r, c = possible_cells[0]
                    explanation = (
                        f"Look at the 3x3 box starting at row {start_row + 1}, column {start_col + 1}. "
                        f"The number {value} must go in row {r + 1}, column {c + 1} "
                        f"because it is the only cell in this box not blocked by another {value}."
                    )
                    return (r, c, value, explanation)

    return None