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

    def _get_broken_columns(self, board):
        broken_cols = []
        for c in range(9):
            col_values = [board[r][c] for r in range(9)]
            if len(set(col_values)) < 9:
                broken_cols.append(c)
        return broken_cols

    def _mutate(self, board, mutation_rate=0.15):
        broken_cols = self._get_broken_columns(board)
        
        for r in range(9):
            if random.random() < mutation_rate:
                movable_cols = [c for c in range(9) if not self.fixed_cells[r][c]]
                
                if len(movable_cols) >= 2:
                    broken_movable = [c for c in movable_cols if c in broken_cols]
                    
                    if broken_movable and len(broken_movable) < len(movable_cols):
                        c1 = random.choice(broken_movable)
                        movable_cols.remove(c1)
                        c2 = random.choice(movable_cols)
                    else:
                        c1, c2 = random.sample(movable_cols, 2)
                        
                    board[r][c1], board[r][c2] = board[r][c2], board[r][c1]
        return board

    def solve(self):
        print(f"Initializing Population ({self.pop_size} boards)...")
        population = [self._create_individual() for _ in range(self.pop_size)]

        stagnation_counter = 0
        previous_best = 999
        
        for generation in range(self.max_generations):
            graded_pop = [(self._calculate_fitness(board), board) for board in population]
            graded_pop.sort(key=lambda x: x[0])
            
            best_fitness = graded_pop[0][0]
            best_board = graded_pop[0][1]

            elite_count = int(self.pop_size * 0.2)
            elites = [item[1] for item in graded_pop[:elite_count]]

            if best_fitness == previous_best:
                stagnation_counter += 1
            else:
                stagnation_counter = 0
                previous_best = best_fitness

            current_mutation = 0.30 if stagnation_counter > 15 else 0.15
            
            if stagnation_counter > 50:
                print(f"Stuck at {best_fitness} errors! Triggering Mass Extinction...")
                population = elites[:2] + [self._create_individual() for _ in range(self.pop_size - 2)]
                stagnation_counter = 0
                continue
            
            if generation % 10 == 0:
                print(f"Generation {generation} | Best Fitness: {best_fitness} | Mut Rate: {current_mutation}")
            
            if best_fitness == 0:
                print(f"\nSUCCESS! Memetic evolution solved the board in {generation} generations!")
                return best_board
            
            next_generation = []
            next_generation.extend(elites[:2]) 
            
            while len(next_generation) < self.pop_size:
                parent1, parent2 = random.sample(elites, 2)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child, mutation_rate=current_mutation)
                next_generation.append(child)
                
            population = next_generation
            
        print("\nEvolution failed to find a perfect solution within the generation limit.")
        return None

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