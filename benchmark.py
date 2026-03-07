import time
from puzzle import Tile, Grid
from search import DFS, AStar
import glob
import os

def puzzle_load(filename):
    """Load puzzle from file."""
    with open(filename, "r") as f:
        rows, cols = map(int, f.readline().split())
        
        grid_data = []
        for _ in range(rows):
            tokens = f.readline().split()
            row_tiles = []
            
            for token in tokens:
                pipe_type = token[0]
                rotation = int(token[1])
                row_tiles.append(Tile(pipe_type, rotation))
            
            grid_data.append(row_tiles)
        
        return Grid(grid_data)

def benchmark_solver(solver_class, puzzle, puzzle_name):
    """Benchmark a solver on a puzzle."""
    solver = solver_class()
    
    # Use a deep copy to avoid modifying the original puzzle
    puzzle_copy = puzzle.deep_copy()
    
    start_time = time.time()
    solution = solver.solve(puzzle_copy)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    
    return {
        'solver': solver_class.__name__,
        'puzzle': puzzle_name,
        'solution_found': solution is not None,
        'nodes_expanded': solver.nodes_expanded,
        'time': elapsed_time
    }

def run_benchmark():
    """Run benchmark on all puzzles with both solvers."""
    puzzle_files = glob.glob("inputs/*.txt")

    puzzles = [
        (file, os.path.splitext(os.path.basename(file))[0])
        for file in puzzle_files
    ]
    
    solvers = [DFS, AStar]
    
    results = []
    
    print("=" * 80)
    print("BENCHMARK RESULTS")
    print("=" * 80)
    print()
    
    for puzzle_file, puzzle_name in puzzles:
        try:
            puzzle = puzzle_load(puzzle_file)
            print(f"Testing puzzle: {puzzle_name}")
            print("-" * 80)
            
            for solver_class in solvers:
                result = benchmark_solver(solver_class, puzzle, puzzle_name)
                results.append(result)
                
                status = "✓ SOLVED" if result['solution_found'] else "✗ FAILED"
                print(f"{result['solver']:15} | {status:12} | "
                      f"Nodes: {result['nodes_expanded']:8} | "
                      f"Time: {result['time']:.4f}s")
            
            print()
        except FileNotFoundError:
            print(f"Warning: {puzzle_file} not found, skipping...")
            print()
    
    # Summary table
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{'Puzzle':<15} {'Solver':<15} {'Status':<12} {'Nodes':<12} {'Time (s)':<12}")
    print("-" * 80)
    
    for result in results:
        status = "SOLVED" if result['solution_found'] else "FAILED"
        print(f"{result['puzzle']:<15} {result['solver']:<15} {status:<12} "
              f"{result['nodes_expanded']:<12} {result['time']:<12.4f}")
    
    print("=" * 80)
    
    # Comparison by puzzle
    print("\nCOMPARISON BY PUZZLE")
    print("=" * 80)
    
    for puzzle_file, puzzle_name in puzzles:
        puzzle_results = [r for r in results if r['puzzle'] == puzzle_name]
        if not puzzle_results:
            continue
        
        print(f"\n{puzzle_name}:")
        dfs_result = next((r for r in puzzle_results if r['solver'] == 'DFS'), None)
        astar_result = next((r for r in puzzle_results if r['solver'] == 'AStar'), None)
        
        if dfs_result and astar_result:
            if dfs_result['nodes_expanded'] > 0 and astar_result['nodes_expanded'] > 0:
                speedup = dfs_result['nodes_expanded'] / astar_result['nodes_expanded']
                time_ratio = dfs_result['time'] / astar_result['time'] if astar_result['time'] > 0 else float('inf')
                
                print(f"  Nodes: DFS={dfs_result['nodes_expanded']}, "
                      f"A*={astar_result['nodes_expanded']} "
                      f"(A* is {speedup:.2f}x more efficient)")
                print(f"  Time:  DFS={dfs_result['time']:.4f}s, "
                      f"A*={astar_result['time']:.4f}s "
                      f"(A* is {time_ratio:.2f}x faster)")
    
    return results

if __name__ == "__main__":
    run_benchmark()
