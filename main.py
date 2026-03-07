from puzzle import Tile,Grid
from search import DFS, AStar
from ui import replay_steps
import os 

def choose_solver():
    while True:
        print("\nChoose a solver:")
        print("1. Depth first search")
        print("2. A* Search")
        choice = input("Enter choice: ")

        if choice == "1":
            return DFS()
        elif choice == "2":
            return AStar()
        else:
            print("Invalid choice. Try again.")

def choose_input():
    while True:
        filename = input("\nEnter testcase name: ")

        path = os.path.join("inputs", filename)

        if os.path.exists(path):
            return path
        else:
            print("File not found in 'inputs/' folder. Try again.")

def puzzle_load(filename):
    with open(filename,"r") as f:
        rows,cols = map(int, f.readline().split())

        grid_data = []
        for _ in range(rows):
            tokens = f.readline().split()
            row_tiles = []

            for token in tokens:
                pipe_type = token[0]
                rotation = int(token[1])
                row_tiles.append(Tile(pipe_type,rotation))

            grid_data.append(row_tiles)

        return Grid(grid_data)
    
def main():
    input_file = choose_input()
    puzzle = puzzle_load(input_file)
    #puzzle.__str__()
    solver = choose_solver()
    
    solution = solver.solve(puzzle)
    
    if solution:
        print("\nSolution found!")
        print("Nodes expanded:", solver.nodes_expanded)
        replay_steps(solver.steps)
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()