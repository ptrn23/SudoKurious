N = 9 # N X N sudoku
import copy
# ==================================================================================
# 
#                                 SUDOKU TECHNIQUES
# 
# ==================================================================================
class move:
    def __init__(self, i, j, hCost, gCost, msg, val):
        self.i = i
        self.j = j
        self.val = val
        self.fCost = hCost + gCost
        self.explanation = msg

    def return_summary(self):
        return (self.i, self.j, self.val, self.explanation)
    
def fill_candidate_board(board, variant = "standard", cages = None):
    filled_candidates = [[None for _ in range(N)] for _ in range(N)]
    for r in range(N):
        for c in range(N):
            if board[r][c] != 0:
                filled_candidates[r][c] = []
                continue
            filled_candidates[r][c] = get_candidates(board, r, c, variant, cages)
    return filled_candidates 

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
                    # board[row][col] = value
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
                board[row][col] = value
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
                board[row][col] = value
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
                    board[r][c] = value
                    return move(r, c, heurestic_cost_fxn(board, variant), 1, explanation, value)

    return None

def find_hidden_single_candidates(board, candidate_board, variant="standard", cages=None):
    
    for i in range(N):
        for j in range(N):
            if len(candidate_board[i][j]) == 1:
                value = next(iter(candidate_board[i][j]))
                explanation = (
                    f"Through elimination of candidates, only one candidate is left "
                    f"for row {i} and col {j} which is {value}"
                )
                board[i][j] = value
                candidate_board = update_candidate_board(candidate_board, value, i, j)
                return move(i, j, heurestic_cost_fxn(board, variant), 1, explanation, value)
# ==================================================================================
# 
#                         CANDIDATE ELEMINATION TECHNIQUES
# 
# ==================================================================================
def naked_pair_elimination(candidate_board, variant="standard", cages=None):
    candidate_board = copy.deepcopy(candidate_board)
    naked_pairs = get_naked_pairs(candidate_board, variant, cages)
    changed = False
    for p1, p2, type in naked_pairs:
        i_r, i_c = p1 
        j_r, j_c = p2 
        if (len(candidate_board[i_r][i_c]) == 2):
            val1, val2 = tuple(candidate_board[i_r][i_c])
        elif len(candidate_board[j_r][j_c]) == 2:
            val1, val2 = tuple(candidate_board[j_r][j_c])
        else:
            print("no naked pair")
            continue
        if type == "Column":
            for r in range(9):
                if r == i_r or r == j_r:
                    continue
                if val1 in candidate_board[r][i_c]:
                    changed = True
                    candidate_board[r][i_c].remove(val1)
                if val2 in candidate_board[r][i_c]:
                    changed = True
                    candidate_board[r][i_c].remove(val2)
        elif type == "Row":
            for c in range(9):
                if c == i_c or c == j_c:
                    continue
                if val1 in candidate_board[i_r][c]:
                    changed = True
                    candidate_board[i_r][c].remove(val1)
                if val2 in candidate_board[i_r][c]:
                    changed = True
                    candidate_board[i_r][c].remove(val2)
        elif type == "Box":
            box_row = (i_r // 3) * 3
            box_col = (i_c // 3) * 3
            for b_r in range(3):
                for b_c in range(3):
                    r = box_row + b_r
                    c = box_col + b_c
                    if (len({(r, c), p1, p2}) == 2):
                        continue
                    if val1 in candidate_board[r][c]:
                        changed = True
                        candidate_board[r][c].remove(val1)
                    if val2 in candidate_board[r][c]:
                        changed = True
                        candidate_board[r][c].remove(val2)
    return (candidate_board, changed)
def pointing_pairs_triples(candidate_board, variant="standard", cages=None):
    candidate_board = copy.deepcopy(candidate_board)
    changed = False
    for b_r in range(3):
        for b_c in range(3):
            digit_pos = {d:[] for d in range(1,10)}
            block_cols = range(b_c*3, b_c*3 + 3)
            block_rows = range(b_r*3, b_r*3 + 3)
            for r in block_rows:
                for c in block_cols:
                    for val in candidate_board[r][c]:
                        digit_pos[val].append((r, c))
            
            for digit, pos in digit_pos.items():
                if (len(pos) < 2):
                    continue
                rows = {p[0]for p in pos}
                cols = {p[1]for p in pos}
                if len(rows) == 1:
                    r = next(iter(rows))
                    for c in range(9):
                        if c not in block_cols and digit in candidate_board[r][c]:
                            candidate_board[r][c].remove(digit)
                            changed = True
                elif len(cols) == 1:
                    c = next(iter(cols))
                    for r in range(9):
                        if r not in block_rows and digit in candidate_board[r][c]:
                            candidate_board[r][c].remove(digit)
                            changed = True
    return (candidate_board, changed)

lst_of_techs = [find_naked_single, find_hidden_single]
lst_of_techs_candidate_elim = [find_hidden_single_candidates]
candidate_elimination_techs = [pointing_pairs_triples, naked_pair_elimination]


                    
# ==================================================================================
# 
#                                    API FUNCTIONS
# 
# ==================================================================================
def check_sudoku(board, variant="standard", cages=None):
    N = 9
    
    # basic sudoku rules
    for box_i in range(0, N, 3):
        for box_j in range(0, N, 3):
            block = []
            loc_in_sudoku = []
            for i in range(box_i+0,box_i+3):
                row = []
                for j in range(box_j+0,box_j+3):
                    row.append(board[i][j])
                    loc_in_sudoku.append((i,j))
                block+=row
            print(block)
            if ((not_unique := getRepeatingNumber(block)) != None):
                return createErrorMsg(not_unique, len(block), loc_in_sudoku, "3x3 box", block)
                
    # 2. Row and Column Check (FIXED STALE LOCATIONS)
    for i in range(N):
        col = []
        col_locs = []
        row = []
        row_locs = []
        for j in range(N):
            col.append(board[j][i])
            col_locs.append((j, i))
            row.append(board[i][j])
            row_locs.append((i, j))
            
        if ((not_unique := getRepeatingNumber(col)) != None):
            return createErrorMsg(not_unique, len(col), col_locs, f"column {i+1}", col)
        
        if ((not_unique := getRepeatingNumber(row)) != None):
            return createErrorMsg(not_unique, len(row), row_locs, f"row {i+1}", row)
    
    if variant == "x-sudoku":
        # \
        leftWing = []
        leftWingLocs = []
        for i in range(N):
            leftWing.append(board[i][i])
            leftWingLocs.append((i, i))
        
        if ((not_unique := getRepeatingNumber(leftWing)) != None):
            return createErrorMsg(not_unique, len(leftWing), leftWingLocs, "main diagonal (\\)", leftWing)
        
        # /
        rightWing = []
        rightWingLocs = []
        for i in range(N):
            rightWing.append(board[i][N-1-i])
            rightWingLocs.append((i, N-1-i))
            
        if ((not_unique := getRepeatingNumber(rightWing)) != None):
            return createErrorMsg(not_unique, len(rightWing), loc_in_sudoku, "Right Wing error", rightWing)
    
    # check if sudoku is complete
    h_cost = 0 # if huerestic cost == 0, then we are at the goal/complete sudoku
    for box_i in range(0, N, 3):
        for box_j in range(0, N, 3):
            block =[]
            for i in range(box_i+0,box_i+3):
                row = []
                for j in range(box_j+0,box_j+3):
                    row.append(board[i][j])
                block.append(row)
            h_cost += box_cost(block)
    for i in range(N):
        col = []
        row = []
        for j in range(N):
            col.append(board[j][i])
            row.append(board[i][j])
        h_cost += row_col_cost(col)
        h_cost += row_col_cost(row)
    
    if h_cost == 0:
        return "Complete Sudoku"
    return None
# ==================================================================================
# 
#                                HUERESTIC FUNCTIONS
# 
# ==================================================================================

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
            for i in range(box_i+0,box_i+3):
                row = []
                for j in range(box_j+0,box_j+3):
                    row.append(board[i][j])
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
    board = copy.deepcopy(board)
    for tech in lst_of_techs:
        tech_res = tech(board, variant, cage)
        if tech_res != None:
            return tech_res
    candidate_board = fill_candidate_board(board, variant, cage)
    for tech in lst_of_techs_candidate_elim:
        changed = True
        while changed:
            changed = False
            for c_board_elim_tech in candidate_elimination_techs:
                candidate_board, res = c_board_elim_tech(candidate_board, variant, cage)
                if res:
                    changed = res
        tech_res  = tech(board, candidate_board, variant, cage)
        if (tech_res != None):
            return tech_res
    return None
            

def a_star(board, variant = "standard", cage = None ):
    curCost = heurestic_cost_fxn(board, variant, cage)
    open_set = []
    closed_set = []
    # while (open_set):
    
    
# ==================================================================================
# 
#                                    HELPER FUNCTIONS
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
    for num, count in arr.items():
        if count > 1 and num != 0:
            return num
    return None 
def getUniqueNumber(arr):
    arr = Counter(arr)
    for num, count in arr.items():
        if count == 1 and num != 0:
            return num
    return None 

def createErrorMsg(errorVal, n, loc, msg, grp):
    error_locs = []
    for i in range(n):
        if grp[i] == errorVal:
            error_locs.append(loc[i])
    print(errorVal, error_locs)
    return incorrectSudoku(error_locs, msg, errorVal)
def find_naked_pair(candidate_board, pairs, type):
    naked_pairs = []
    for i in range(len(pairs)):
        i_r, i_c = pairs[i]
        i_vals = set(candidate_board[i_r][i_c])
        for j in range(i+ 1,len(pairs)):
            j_r, j_c = pairs[j]
            j_vals = set(candidate_board[j_r][j_c])
            if (i_vals == j_vals):
                naked_pairs.append(((i_r, i_c), (j_r, j_c), type))
                break
    return naked_pairs
def update_candidate_board(candidate_board, value, i, j):
    candidate_board[i][j] = set()
    # column
    for r in range(9):
        if r == i :
            continue
        if value in candidate_board[r][j]:
            candidate_board[r][j].remove(value)
    # row
    for c in range(9):
        if c == j:
            continue
        if value in candidate_board[i][c]:
            candidate_board[i][c].remove(value)
    # box
    box_row = (i // 3) * 3
    box_col = (j // 3) * 3
    for b_r in range(3):
        for b_c in range(3):
            r = box_row + b_r
            c = box_col + b_c
            if i == r and j == c:
                continue
            if value in candidate_board[r][c]:
                candidate_board[r][c].remove(value)
    return candidate_board

def get_naked_pairs(candidate_board, variant="standard", cages=None):
    naked_pairs = []
    # block naked pairs
    for b_r in range(3):
        for b_c in range(3):
            block_cols = range(b_c*3, b_c*3 + 3)
            block_rows = range(b_r*3, b_r*3 + 3)
            pairs = [(r, c) for r in block_rows for c in block_cols if len(candidate_board[r][c]) == 2]
            if len(pairs) < 2:
                continue
            naked_pairs += find_naked_pair(candidate_board, pairs, "Box")
    # column
    for c in range(9):
        pairs = [(r, c) for r in range(9) if len(candidate_board[r][c]) == 2]
        if len(pairs) < 2:
            continue
        naked_pairs += find_naked_pair(candidate_board, pairs, "Column")
    # row
    for r in range(9):
        pairs = [(r, c) for c in range(9) if len(candidate_board[r][c]) == 2]
        if len(pairs) < 2:
            continue
        naked_pairs += find_naked_pair(candidate_board, pairs, "Row")
    return naked_pairs 

def print_candidates(candidates):
    cell_width = 11  # "{1,2,3,4,5,6,7,8,9}" = 11 chars max

    h_divider = "+" + (("-" * (cell_width * 3 + 2)) + "+") * 3

    for row in range(9):
        if row % 3 == 0:
            print(h_divider)

        line = ""
        for col in range(9):
            if col % 3 == 0:
                line += "| "
            cell = candidates[row][col]
            content = "{" + ",".join(str(d) for d in sorted(cell)) + "}" if cell else "  .  "
            line += content.ljust(cell_width)
        line += "|"
        print(line)

    print(h_divider)

    
    
from pprint import pprint
if __name__ == "__main__":
    test_case0 = {
        "grid": [
            [5,3,0,0,7,0,0,0,0],
            [6,0,0,1,9,5,0,0,0],
            [0,9,8,0,0,0,0,6,0],
            [8,0,0,0,6,0,0,0,3],
            [4,0,0,8,0,3,0,0,1],
            [7,0,0,0,2,0,0,0,6],
            [0,6,0,0,0,0,2,8,0],
            [0,0,0,4,1,9,0,0,5],
            [0,0,0,0,8,0,0,7,9]
        ],
        "sol":[
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 9, 3],
            [4, 2, 6, 8, 5, 3, 7, 2, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]
    }
    test_grid = [
       
    ]
    
    test_case1 = {
        "grid": [
            [7,0,0,   4,0,9,   0,0,0],
            [0,0,0,   0,7,5,   3,0,0],
            [0,5,0,   1,0,0,   0,7,0],
            
            [6,4,0,   0,0,0,   0,1,0],
            [1,0,0,   0,8,0,   0,0,4],
            [0,9,0,   0,0,0,   0,3,6],
            
            [0,2,0,   0,0,4,   0,6,0],
            [0,0,7,   9,5,0,   0,0,0],
            [0,0,0,   7,0,8,   0,0,5]
        ],
        "sol":[
            [7, 3, 1, 4, 6, 9, 5, 8, 2],
            [2, 6, 9, 8, 7, 5, 3, 4, 1],
            [8, 5, 4, 1, 3, 2, 6, 7, 9],
            [6, 4, 3, 5, 9, 7, 2, 1, 8],
            [1, 7, 2, 6, 8, 3, 9, 5, 4],
            [5, 9, 8, 2, 4, 1, 7, 3, 6],
            [9, 2, 5, 3, 1, 4, 8, 6, 7],
            [4, 8, 7, 9, 5, 6, 1, 2, 3],
            [3, 1, 6, 7, 2, 8, 4, 9, 5]
        ]
    }
    test_case2 = {
        "grid": [
            [0,3,0,   0,0,7,   0,0,0],
            [0,6,7,   1,0,0,   3,5,0],
            [0,1,9,   0,0,0,   0,0,0],
            
            [5,0,0,   0,0,0,   0,0,7],
            [0,7,0,   2,0,3,   0,1,0],
            [9,0,0,   0,0,0,   0,0,8],
            
            [0,0,0,   0,0,0,   6,8,0],
            [0,8,6,   0,0,2,   9,7,0],
            [0,0,0,   7,0,0,   0,4,0]
        ],

        "sol":[
            [2, 3, 5, 4, 6, 7, 8, 9, 1],
            [8, 6, 7, 1, 2, 9, 3, 5, 4],
            [4, 1, 9, 8, 3, 5, 7, 2, 6],
            [5, 4, 3, 9, 1, 8, 2, 6, 7],
            [6, 7, 8, 2, 5, 3, 4, 1, 9],
            [9, 2, 1, 6, 7, 4, 5, 3, 8],
            [7, 5, 4, 3, 9, 1, 6, 8, 2],
            [1, 8, 6, 5, 4, 2, 9, 7, 3],
            [3, 9, 2, 7, 8, 6, 1, 4, 5]
        ]
    }
    test_case3 = {
        "grid": [[5, 9, 0, 0, 0, 0, 3, 4, 0],
 [0, 0, 4, 0, 5, 0, 0, 0, 0],
 [0, 0, 2, 4, 0, 6, 0, 0, 0],
 [9, 0, 0, 5, 0, 3, 8, 7, 4],
 [4, 5, 0, 0, 1, 8, 0, 3, 0],
 [0, 8, 0, 0, 9, 4, 0, 6, 5],
 [0, 0, 5, 0, 8, 2, 0, 9, 1],
 [0, 0, 9, 0, 0, 0, 0, 0, 3],
 [6, 0, 0, 0, 0, 0, 0, 0, 1]]
    }
    ret = get_best_h_move(test_case3["grid"])
    print(ret.return_summary())
    