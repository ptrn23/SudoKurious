N = 9 # N X N sudoku
class move:
    def __init__(self, i, j, hCost, gCost, msg, val):
        self.i = i
        self.j = j
        self.val = val
        self.fCost = hCost + gCost
        self.explanation = msg

    def return_summary(self):
        return (self.i, self.j, self.val, self.explanation)
    
    
# ==================================================================================
# 
#                                 SUDOKU TECHNIQUES
# 
# ==================================================================================

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
                    return move(row, col, heurestic_cost_fxn(board, variant), 1, explanation, value)

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
                return move(row, col, heurestic_cost_fxn(board, variant), 1, explanation, value)

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
                return move(row, col, heurestic_cost_fxn(board, variant), 1, explanation, value)

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
                    return move(r, c, heurestic_cost_fxn(board, variant), 1, explanation, value)

    return None

lst_of_techs = [find_naked_single, find_hidden_single]

# ==================================================================================
# 
#                                HUERESTIC FUNCTIONS
# 
# ==================================================================================
from collections import Counter
class incorrectSudoku:
    def __init__(self, locs, msg, val):
        self.locs =locs
        self.val = val
        self.explanation = msg

    def return_summary(self):
        return (self.locs, self.val, self.explanation)
    

def getRepeatingNumber(arr):
    arr = Counter(arr)
    print(arr.items())
    for num, count in arr.items():
        if count > 1 and num != 0:
            return num
    return None 

def createErrorMsg(errorVal, n, loc, msg, grp):
    error_locs = []
    for i in range(n):
        if grp[i] == errorVal:
            error_locs.append(loc[i])
    print(errorVal, error_locs)
    return incorrectSudoku(error_locs, msg, errorVal)

def check_sudoku(board, variant="standard", cages=None):
    
    # basic sudoku rules
    for box_i in range(0, N, 3):
        for box_j in range(0, N, 3):
            block =[]
            loc_in_sudoku = []
            for i in range(0,3):
                row = []
                for j in range(0,3):
                    row.append(board[box_i+i][box_j+j])
                    loc_in_sudoku.append((box_i+i,box_j+j))
                block+=row
            print(block)
            if ((not_unique := getRepeatingNumber(block)) != None):
                return createErrorMsg(not_unique, len(block), loc_in_sudoku, "Both in the same block", block)
                
    for i in range(N):
        col = []
        row = []
        for j in range(N):
            col.append(board[j][i])
            row.append(board[i][j])
            
        if ((not_unique := getRepeatingNumber(col)) != None):
            return createErrorMsg(not_unique, len(col), loc_in_sudoku, "Both in the same column", col)
        
        if ((not_unique := getRepeatingNumber(row)) != None):
            return createErrorMsg(not_unique, len(row), loc_in_sudoku, "Both in the same row", row)
    
    if variant == "x-sudoku":
        leftWing = [] #\
        rightWing = [] # /
        for i in range(0,N):
            # \ wing
            leftWing.append(board[i][i])
            # / wing
            rightWing.append(board[i][N-1-i])
        
        if ((not_unique := getRepeatingNumber(leftWing)) != None):
            return createErrorMsg(not_unique, len(leftWing), loc_in_sudoku, "Left Wing error", leftWing)
        
        if ((not_unique := getRepeatingNumber(rightWing)) != None):
            return createErrorMsg(not_unique, len(rightWing), loc_in_sudoku, "Right Wing error", rightWing)
    
    # check if sudoku is complete
    h_cos = 0 # if huerestic cost == 0, then we are at the goal/complete sudoku
    for box_i in range(0, N, 3):
        for box_j in range(0, N, 3):
            block =[]
            for i in range(0,3):
                row = []
                for j in range(0,3):
                    row.append(board[box_i+i][box_j+j])
                block.append(row)
            h_cos += box_cost(block)
    for i in range(N):
        col = []
        row = []
        for j in range(N):
            col.append(board[j][i])
            row.append(board[i][j])
        h_cos += row_col_cost(col)
        h_cos += row_col_cost(row)
    
    if h_cos == 0:
        return "Complete Sudoku"
    return None

def box_cost(box):
    res = 0
    flatten = [num for row in box for num in row]
    cost = len(set(flatten))
    return 9 - cost

def row_col_cost(line):
    return 9 - len(set(line))

                
def heurestic_cost_fxn(board, variant = "standard"):
    cost = 0
    for box_i in range(0, 9, 3):
        for box_j in range(0, 9, 3):
            block =[]
            for i in range(0,3):
                row = []
                for j in range(0,3):
                    row.append(board[box_i+i][box_j+j])
                block.append(row)
            cost+= box_cost(block)
    for i in range(9):
        col = []
        row = []
        for j in range(9):
            col.append(board[j][i])
            row.append(board[i][j])
        cost+= row_col_cost(col) + row_col_cost(row)
    return cost 

def get_best_h_move(board, variant = "standard", cage = None):
    for tech in lst_of_techs:
        tech_res = tech(board, variant, cage)
        if tech_res != None:
            return tech_res
    return None
            

def a_star(board, variant = "standard" ):
    curCost = heurestic_cost_fxn(board, variant, cage)
    open_set = []
    closed_set = []
    # while (open_set):


# box_cost([[1,2,3], [1,2,3], [1,2,3]])
# ifCorrectGrid([
#   [1, 2, 3, 4, 5, 6, 7, 8, 9],
#   [4, 5, 6, 7, 8, 9, 1, 2, 3],
#   [7, 8, 9, 1, 2, 3, 4, 5, 6],
#   [2, 3, 4, 5, 6, 7, 8, 9, 1],
#   [5, 6, 7, 8, 9, 1, 2, 3, 4],
#   [8, 9, 1, 2, 3, 4, 5, 6, 7],
#   [3, 4, 5, 6, 7, 8, 9, 1, 2],
#   [6, 7, 8, 9, 1, 2, 3, 4, 5],
#   [9, 1, 2, 3, 4, 5, 6, 7, 8]
# ])
# 00 01 02    03 04 05 
# 10 11 12    13 14 15
# 20 21 22    23 24 25