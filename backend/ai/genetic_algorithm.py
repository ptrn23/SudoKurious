import random
import copy

class GeneticSudokuSolver:
    def __init__(self, original_board, variant="standard", cages=None, pop_size=100, max_generations=1000):
        self.original_board = original_board
        self.variant = variant
        self.cages = cages
        self.pop_size = pop_size
        self.max_generations = max_generations
        self.fixed_cells = self._get_fixed_cells()
        self.hall_of_fame = [] 

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
    
    def _crossover(self, parent1, parent2):
        child = []
        for r in range(9):
            if random.random() < 0.5:
                child.append(copy.deepcopy(parent1[r]))
            else:
                child.append(copy.deepcopy(parent2[r]))
        return child

    def _get_conflicting_cells(self, board):
        conflicts = set()
        
        for c in range(9):
            seen = {}
            for r in range(9):
                val = board[r][c]
                if val in seen:
                    conflicts.add((r, c))
                    conflicts.add((seen[val], c))
                else:
                    seen[val] = r
                    
        for box_r in range(3):
            for box_c in range(3):
                seen = {}
                for i in range(3):
                    for j in range(3):
                        r, c = box_r * 3 + i, box_c * 3 + j
                        val = board[r][c]
                        if val in seen:
                            conflicts.add((r, c))
                            conflicts.add(seen[val])
                        else:
                            seen[val] = (r, c)
                            
        return conflicts

    def _mutate(self, board, mutation_rate=0.15):
        conflicts = self._get_conflicting_cells(board)
        
        for r in range(9):
            if random.random() < mutation_rate:
                movable_cols = [c for c in range(9) if not self.fixed_cells[r][c]]
                
                if len(movable_cols) >= 2:
                    conflicting_movable = [c for c in movable_cols if (r, c) in conflicts]
                    
                    if conflicting_movable and len(conflicting_movable) < len(movable_cols):
                        c1 = random.choice(conflicting_movable)
                        movable_cols.remove(c1)
                        c2 = random.choice(movable_cols)
                    else:
                        c1, c2 = random.sample(movable_cols, 2)
                        
                    board[r][c1], board[r][c2] = board[r][c2], board[r][c1]
        return board

    def _local_search(self, board, max_attempts=5):
        current_fitness = self._calculate_fitness(board)
        if current_fitness == 0:
            return board

        conflicts = list(self._get_conflicting_cells(board))
        if not conflicts:
            return board
        
        random.shuffle(conflicts)

        for r, c1 in conflicts[:max_attempts]:
            if self.fixed_cells[r][c1]: 
                continue

            movables_in_row = [c for c in range(9) if not self.fixed_cells[r][c] and c != c1]
            
            for c2 in movables_in_row:
                board[r][c1], board[r][c2] = board[r][c2], board[r][c1]
                new_fitness = self._calculate_fitness(board)

                if new_fitness < current_fitness:
                    return board 
                
                board[r][c1], board[r][c2] = board[r][c2], board[r][c1]

        return board

    def _update_hall_of_fame(self, graded_pop):
        for fitness, board in graded_pop:
            if fitness <= 4:
                self.hall_of_fame.append(copy.deepcopy(board))
        
        if len(self.hall_of_fame) > 50:
            self.hall_of_fame = self.hall_of_fame[-50:]

    def _get_consensus_hint(self):
        if not self.hall_of_fame:
            return None

        agreement_cells = []

        for r in range(9):
            for c in range(9):
                if self.fixed_cells[r][c]:
                    continue
                
                values_at_pos = [board[r][c] for board in self.hall_of_fame]
                if len(set(values_at_pos)) == 1:
                    agreement_cells.append((r, c, values_at_pos[0]))

        if agreement_cells:
            return random.choice(agreement_cells)
        return None

    def solve(self):
        population = [self._create_individual() for _ in range(self.pop_size)]
        previous_best = 999
        stagnation_counter = 0
        
        for generation in range(self.max_generations):
            graded_pop = [(self._calculate_fitness(board), board) for board in population]
            graded_pop.sort(key=lambda x: x[0])
            
            best_fitness = graded_pop[0][0]
            best_board = graded_pop[0][1]
            self._update_hall_of_fame(graded_pop[:5])
            if best_fitness <= 2:
                print(f"Stalled at {best_fitness} errors. Extracting consensus hint...")
                return best_board 

            if best_fitness == previous_best:
                stagnation_counter += 1
            else:
                stagnation_counter = 0
                previous_best = best_fitness

            if stagnation_counter > 20:
                population = [graded_pop[0][1], graded_pop[1][1]] + [self._create_individual() for _ in range(self.pop_size - 2)]
                stagnation_counter = 0
                continue

            elite_count = int(self.pop_size * 0.4)
            elites = [item[1] for item in graded_pop[:elite_count]]
            next_generation = elites[:2]

            while len(next_generation) < self.pop_size:
                p1, p2 = random.sample(elites, 2)
                child = self._mutate(self._crossover(p1, p2))
                child = self._local_search(child)
                next_generation.append(child)
                
            population = next_generation
            
        return graded_pop[0][1]

    def get_hint_result(self):
        best_found = self.solve()
        hint = self._get_consensus_hint()
        
        if hint:
            r, c, val = hint
            return r, c, val, best_found
        
        # if no consensus, just pick a random empty cell from best_found
        empty_cells = [(r, c) for r in range(9) for c in range(9) if not self.fixed_cells[r][c]]
        r, c = random.choice(empty_cells)
        return r, c, best_found[r][c], best_found

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

if __name__ == "__main__":
    test_grid = [
        [5,3,0,0,7,0,0,0,0],
        [6,0,0,1,9,5,0,0,0],
        [0,9,8,0,0,0,0,6,0],
        [8,0,0,0,6,0,0,0,3],
        [4,0,0,8,0,3,0,0,1],
        [7,0,0,0,2,0,0,0,6],
        [0,6,0,0,0,0,2,8,0],
        [0,0,0,4,1,9,0,0,5],
        [0,0,0,0,8,0,0,7,9]
    ]
    
    ga = GeneticSudokuSolver(test_grid, pop_size=200, max_generations=5000)
    
    import time
    start = time.time()
    solution = ga.solve()
    end = time.time()
    
    if solution:
        print(f"\nTime taken: {end - start:.2f} seconds")
        print("Final Solved Board:")
        for row in solution:
            print(row)