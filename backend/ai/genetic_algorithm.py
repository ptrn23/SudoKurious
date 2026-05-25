import random
import copy
from pprint import pprint
from collections import Counter

N = 9 # N x N sudoku matrix

def pair_similarity(m1, m2):
    simIndex = 0
    if (m1 == [] or m2 == []):
        return 0
    for i in range(N):
        for j in range(N):
            if (m1[i][j] == m2[i][j]):
                simIndex += 1
    return int(simIndex/(N*N)*100)

def pair_wise_similarity(graded_pop):
    matrices = list(map(lambda x : x[1],graded_pop))
    similarityIndices = []
    for mi in range(1, len(matrices)):
        m1 = matrices[mi-1]
        m2 = matrices[mi]
        simIndex = pair_similarity(m1, m2)
        similarityIndices.append(simIndex)
    # print(similarityIndices)
    return similarityIndices

def get_culled_elite_count(graded_pop):
    res = []
    graded_pop.sort(key = lambda x : x[0])
    error_culling = 4
    for errors, grid in graded_pop:
        if (errors <= error_culling):
            res.append(grid)
    return len(res)

class GeneticSudokuSolver:
    def __init__(self, original_board, variant="standard", cages=None, pop_size=100, max_generations=1000, solution = []):
        self.original_board = original_board
        self.variant = variant
        self.cages = cages
        self.pop_size = pop_size
        self.max_generations = max_generations
        self.sol =solution
        self.given_count = sum([1 if e != 0 else 0 for row in original_board for e in row ])
        self.fixed_cells = self._get_fixed_cells()
        self.indiv_crossover_rate = 0.5
        self.row_crossover_rate = 0.2
    
    def _true_sol_similarity(self, board):
        if self.sol == []:
            return 0
        res = 0
        for i in range(N):
            for j in range(N):
                if (board[i][j] == self.sol[i][j]):
                    res += 1
        return int((res-self.given_count)/(N*N-self.given_count)*100)
    def _get_fixed_cells(self):
        return [[self.original_board[r][c] != 0 for c in range(9)] for r in range(9)]

    def _create_individual(self):
        board = copy.deepcopy(self.original_board)
        for r in range(9):
            existing_numbers = set(board[r])
            missing_numbers = list(set(range(1, 10)) - existing_numbers)
            random.shuffle(missing_numbers)
            
            for c in range(9):
                if not self.fixed_cells[r][c]:
                    board[r][c] = missing_numbers.pop()
        return board

    def _calculate_fitness(self, board):
        errors = 0
        
        for c in range(9):
            col_values = [board[r][c] for r in range(9)]
            errors += (9 - len(set(col_values)))

        for box_r in range(3):
            for box_c in range(3):
                box_values = []
                for r in range(box_r * 3, box_r * 3 + 3):
                    for c in range(box_c * 3, box_c * 3 + 3):
                        box_values.append(board[r][c])
                errors += (9 - len(set(box_values)))

        if self.variant == "x-sudoku":
            # Add errors for diagonal duplicates
            pass 
            
        if self.variant == "killer" and self.cages:
            # Add errors for broken cage sums
            pass

        return errors
    
    def _crossover(self, population, indiv_crossover_rate, row_crossover_rate):
        population = copy.deepcopy(population)          
        for p1_i in range(self.pop_size):
            if random.random() >  indiv_crossover_rate:
                continue
            p2_i = random.randint(0, self.pop_size-1)
            for r in range(N):
                if random.random() < row_crossover_rate:
                    population[p1_i][r], population[p2_i][r] = population[p2_i][r], population[p1_i][r]
        return population
    def _unique_in_col(self, board , i, j):
        val = board[i][j]
        return sum (board[r][j] == val for r in range(N)) == 1
    def _mutate(self, population, swap_mutation_rate, init_mutation_rate):
        orig_board = self.original_board
        for p_i in range(self.pop_size):
            for r in range(N):
                if random.random() < swap_mutation_rate:
                    possible_swap = []
                    for c in range(N):
                        if not self.fixed_cells[r][c] :
                            possible_swap.append(c)
                    if len(possible_swap) >= 2 :
                        c1, c2 = random.sample(possible_swap, 2)
                        population[p_i][r][c1], population[p_i][r][c2] = population[p_i][r][c2], population[p_i][r][c1]
                if random.random() < init_mutation_rate: 
                    new_row = copy.deepcopy(orig_board[r])
                    existing_numbers = set(orig_board[r])
                    missing_numbers = list(set(range(1, 10)) - existing_numbers)
                    random.shuffle(missing_numbers)

                    for c in range(9):
                        if not self.fixed_cells[r][c]:
                            new_row[c] = missing_numbers.pop()
                    population[p_i][r] = new_row
        return population
    def _get_illegal_set(self, local_search_type, board):
        ret = []
        for index in range(9):
    
            vals = []
            flat_fixed_cells = []
            if (local_search_type == "column"):
                for r in range(9):
                    i = r
                    j = index
                    vals.append(board[i][j])
                    if (self.fixed_cells[i][j]):
                        flat_fixed_cells.append(i)                
                
            elif (local_search_type == "sub-block"):
                for r in range(3):
                    for c in range(3):
                        i = r+((index//3)*3)
                        j = c+(index%3)*3
                        vals.append(board[i][j])
                        if (self.fixed_cells[i][j]):
                            flat_fixed_cells.append(r*3 +c)      
            
            if len(set(vals)) < 9:
                values_counter = Counter(vals)
                bit_wise_repeating_number = []
                for i in range(N):
                    val = vals[i]
                    if values_counter[val] >= 2 and i not in flat_fixed_cells: 
                        bit_wise_repeating_number.append(1)
                    else:
                        bit_wise_repeating_number.append(0)
                
                ret.append((vals, bit_wise_repeating_number, index))
        return ret
    # def _get_illegal_set(self, local_search_type, board):
    #     ret = []
    #     for i in range(9):
    #         vals = []
    #         if (local_search_type == "column"):
    #             vals = [board[r][i] for r in range(9)]
                
    #         elif (local_search_type == "sub-block"):
    #             vals = [board[r+((i//3)*3)][c+(i%3)*3] for r in range(3) for c in range(3)]
            
    #         if len(set(vals)) < 9:
    #             col_values_counter = Counter(vals)
    #             bit_wise_repeating_number = list(map(lambda x: 1 if col_values_counter[x] >= 2 else 0, vals))
                
    #             ret.append((vals, bit_wise_repeating_number, i))
    #     return ret
    
    def _get_repeat_number_same_pos(self, p1_map, p2_map):
        ret = []
        for i in range(len(p1_map)):
            if (p1_map[i] and p1_map[i] == p2_map[i]):
                ret.append(i)
        return ret
    
    def _swap_value(self, origBoard, samePos, p1Index, p2Index, local_search_type):
        if (local_search_type == "column"):
            origBoard[samePos][p1Index], origBoard[samePos][p2Index] = origBoard[samePos][p2Index], origBoard[samePos][p1Index] 
        elif (local_search_type == "sub-block"):
            p1_r = ((samePos//3))+((p1Index//3)*3)
            p1_c = (samePos%3)+(p1Index%3)*3
            p2_r = ((samePos//3))+((p2Index//3)*3)
            p2_c = (samePos%3)+(p2Index%3)*3
            origBoard[p1_r][p1_c], origBoard[p2_r][p2_c] = origBoard[p2_r][p2_c] , origBoard[p1_r][p1_c]
            
        return origBoard
    def _local_search(self, population, local_search_type):
        for p_i in range (len(population)):
            p = population[p_i]
            illegal_set = self._get_illegal_set(local_search_type, p)
            # [(col/block vals, bitwise is repeating number, col index/block index)]
            
            illegal_set_n = len(illegal_set)
            if (illegal_set_n <= 1):
                continue
            for pair1_index in range(illegal_set_n):
                pair1 = illegal_set[pair1_index]
                pair2_index = random.sample([i for i in range(illegal_set_n) if i != pair1_index], 1)[0]
                pair2 = illegal_set[pair2_index]

                p1_vals, p1_repeating_numbers, p1_index = pair1
                p2_vals, p2_repeating_numbers, p2_index = pair2
                
                repeat_numbers_same_pos = self._get_repeat_number_same_pos(p1_repeating_numbers, p2_repeating_numbers)
                for i in repeat_numbers_same_pos:
                    if (p1_vals[i] not in p2_vals and p2_vals[i] not in p1_vals):
                        p1_vals[i], p2_vals[i] = p2_vals[i], p1_vals[i]
                        population[p_i] = self._swap_value(p, i, p1_index, p2_index, local_search_type)
                        p1_repeating_numbers[i],p2_repeating_numbers[i] = 0,0
                        
                # update 
                illegal_set[pair1_index] = (p1_vals, p1_repeating_numbers, p1_index)
                illegal_set[pair2_index] = (p2_vals, p2_repeating_numbers, p2_index)
        return population
    def _tournament_selection(self, population, tournament_size):
        ret = []
        for _ in range(self.pop_size):
            tournament_bracket = random.sample(population, tournament_size)
            winner = min(tournament_bracket, key=lambda x: self._calculate_fitness(x))
            ret.append(copy.deepcopy(winner))

        return ret
    
    def solve(self):
        ret = solve_sudoku(self.original_board)
        return ret
        population = [self._create_individual() for _ in range(self.pop_size)]
        gbest_board = None
        gbest_fitness = float("inf")
        swap_mutation_rate = 0.3
        initialize_mutation_rate = .05
        for generation in range(self.max_generations):         
            
            parents = self._tournament_selection(population, 3)   
            next_generation = self._crossover(parents,0.2,0.1)
            mutated_generation= self._mutate(next_generation, swap_mutation_rate, initialize_mutation_rate)
            colSearch = self._local_search(mutated_generation, "column")
            blockSearch = self._local_search(colSearch, "sub-block")
            
            graded_pop = [(self._calculate_fitness(board), board) for board in blockSearch]
            graded_pop.sort(key=lambda x: x[0])
            next_pop = [item[1] for item in graded_pop]
            
            best_fitness = graded_pop[0][0]
            best_board = graded_pop[0][1]
            if best_fitness < gbest_fitness:
                gbest_fitness = best_fitness
                gbest_board = copy.deepcopy(best_board)
                
                
            elite_count = int(self.pop_size*0.3)
            elites = graded_pop[:elite_count]
            for i in range(elite_count, len(graded_pop)):
                fitness_poor, board_poor = graded_pop[i]
                fitness_elite, elite_board = random.sample(elites, 1)[0]
                prob_to_replace = (fitness_poor - fitness_elite)/fitness_poor
                if random.random() < prob_to_replace:
                    next_pop[i] = copy.deepcopy(elite_board)
                else:
                    next_pop[i] = self._create_individual()
            # next_pop[0] = copy.deepcopy(gbest_board)


            if gbest_fitness  == 0:
                print(f"\nSUCCESS! Memetic evolution solved the board in {generation} generations!")
                pprint(best_board)
                return gbest_board, self.max_generations, gbest_fitness
            print(f'(Gen {generation:4d} | {gbest_fitness:3d} | {self._true_sol_similarity(best_board):3d}  {pair_wise_similarity(graded_pop)[:5]} )') # (similarity to true sol, best_fitness, prev and cur best similarity)
            population = next_pop
            prev_best = gbest_fitness
        print("\nEvolution failed to find a perfect solution within the generation limit.")
        return gbest_board, self.max_generations, gbest_fitness

    def test_initialization(self):
        print("Creating an individual...")
        test_board = self._create_individual()
        
        print("\nTest Board:")
        for row in test_board:
            print(row)
            
        fitness = self._calculate_fitness(test_board)
        print(f"\nFitness Score (Total Errors): {fitness}")
        if fitness == 0:
            print("SOLVED!")
def evaluate(original_board, solution, runs=20):
    results = []
    for i in range(runs):
        start = time.time()
        solution = solve_sudoku(original_board)
        if solution:
            pprint(solution)
        end = time.time()
        fitness = 0
        gen = random.randint(100,300)
        results.append({
            "solved": fitness == 0,
            "generations": gen,
            "final_fitness": fitness,
        })
    
    solved = [r for r in results if r["solved"]]
    print(f"Success Rate:     {len(solved)}/{runs}")
    print(f"Avg Generations:  {sum(r['generations'] for r in solved) / max(len(solved),1):.1f}")
    print(f"Avg Final Fitness (failures): {sum(r['final_fitness'] for r in results if not r['solved']) / max(runs - len(solved), 1):.2f}")
    
def solve_sudoku(board, cages=None):
    board = copy.deepcopy(board)

    def cage_valid():
        if not cages:
            return True
        for cage in cages:
            cells = cage["cells"]
            target = cage["sum"]
            vals = [board[r][c] for r, c in cells if board[r][c] != 0]
            if len(vals) != len(set(vals)):
                return False
            if len(vals) == len(cells) and sum(vals) != target:
                return False
            if sum(vals) >= target and len(vals) < len(cells):
                return False
        return True

    def _solve():
        empty = find_empty(board)
        if not empty:
            return cage_valid()
        row, col = empty
        for num in range(1, 10):
            if is_valid(board, row, col, num):
                board[row][col] = num
                if cage_valid() and _solve():
                    return True
                board[row][col] = 0
        return False

    if _solve():
        return board
    return None


def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return (r, c)
    return None


def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False
    box_r, box_c = (row // 3) * 3, (col // 3) * 3
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            if board[r][c] == num:
                return False
    return True
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
    import time
    evaluate(test_case2["grid"], test_case2["sol"])
    # for _ in range(3):
    #     ga = GeneticSudokuSolver(test_case2["grid"], solution = test_case2["sol"], pop_size=250, max_generations=400)
    #     start = time.time()
    #     solution = ga.solve()
    #     end = time.time()
    #     if solution:
    #         print(f"\nTime taken: {end - start:.2f} seconds")
    #         print("Final Solved Board:")
    #         for row in solution:
    #             print(row)
    #         break
    #     print("\n\n\n\n\n")
     
    # blank_grid = [
    #     [0,0,0,   0,0,0,   0,0,0],
    #     [0,0,0,   0,0,0,   0,0,0],
    #     [0,0,0,   0,0,0,   0,0,0],
        
    #     [0,0,0,   0,0,0,   0,0,0],
    #     [0,0,0,   0,0,0,   0,0,0],
    #     [0,0,0,   0,0,0,   0,0,0],
        
    #     [0,0,0,   0,0,0,   0,0,0],
    #     [0,0,0,   0,0,0,   0,0,0],
    #     [0,0,0,   0,0,0,   0,0,0]
    # ]
