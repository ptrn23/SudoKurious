def get_candidates(board, row, col, variant="standard", cages=None):
    if board[row][col] != 0:
        return set()

    candidates = set(range(1, 10))
    candidates -= set(board[row])
    candidates -= set(board[r][col] for r in range(9))

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            candidates.discard(board[r][c])

    if variant == "x-sudoku":
        if row == col:
            for i in range(9):
                candidates.discard(board[i][i])
        if row + col == 8:
            for i in range(9):
                candidates.discard(board[i][8 - i])
                
    if variant == "killer" and cages:
        for cage in cages:
            cage_cells = cage.cells if hasattr(cage, 'cells') else cage['cells']
            
            if [row, col] in cage_cells:
                for r, c in cage_cells:
                    candidates.discard(board[r][c])
                break

    return candidates


def find_naked_single(board, variant="standard", cages=None):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                candidates = get_candidates(board, row, col, variant, cages)
                
                if len(candidates) == 1:
                    value = candidates.pop()
                    explanation = (
                        f"Look at row {row + 1}, column {col + 1}. "
                        f"Based on the standard and {variant} variant rules, "
                        f"the only possible number that can fit here is {value}."
                    )
                    return (row, col, value, explanation)

    return None

def find_hidden_single(board, variant="standard", cages=None):
    # check rows
    for row in range(9):
        for value in range(1, 10):
            possible_cols = []
            for col in range(9):
                if board[row][col] == 0 and value in get_candidates(board, row, col, variant, cages):
                    possible_cols.append(col)
                    
            if len(possible_cols) == 1:
                col = possible_cols[0]
                explanation = (
                    f"Look at row {row + 1}. "
                    f"The number {value} can only be placed in column {col + 1} "
                    f"because all other empty cells are blocked by the {variant} rules."
                )
                return (row, col, value, explanation)

    # check columns
    for col in range(9):
        for value in range(1, 10):
            possible_rows = []
            for row in range(9):
                if board[row][col] == 0 and value in get_candidates(board, row, col, variant, cages):
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
                        if board[r][c] == 0 and value in get_candidates(board, r, c, variant, cages):
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