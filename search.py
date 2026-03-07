import heapq
from puzzle import OPPOSITE, DIRS

class DFS:
    def __init__(self):
        self.nodes_expanded = 0
        self.steps = []
    
    def solve(self,grid):
        return self._dfs(grid,0)
    
    def _dfs(self, grid, index):

        self.nodes_expanded += 1

        if index == grid.rows * grid.cols:
            if grid.is_goal():
                self.steps.append((grid.deep_copy(), None, "done", None))
                return grid
            return None

        r = index // grid.cols
        c = index % grid.cols

        original_rotation = grid.grid[r][c].rotation

        for rot in range(4):
            grid.grid[r][c].rotation = rot

            self.steps.append((grid.deep_copy(), (r, c), "try", rot))

            if grid.partial_valid(r, c):
                result = self._dfs(grid, index + 1)
                if result:
                    return result

        self.steps.append((grid.deep_copy(), (r, c), "backtrack", None))

        grid.grid[r][c].rotation = original_rotation
        return None

class AStar:
    def __init__(self):
        self.nodes_expanded = 0
        self.steps = []
    
    def heuristic(self, grid):
        """
        Admissible heuristic function that estimates the cost to reach the goal.
        Returns a lower bound on the number of rotations needed.
        """
        # Count mismatched connections (each mismatch requires at least one rotation to fix)
        mismatches = 0
        
        for r in range(grid.rows):
            for c in range(grid.cols):
                dirs = grid.get_connections(r, c)
                
                for d in dirs:
                    dr, dc = DIRS[d]
                    nr = r + dr
                    nc = c + dc
                    
                    # Out of bounds - this is a leak, needs fixing
                    if not (0 <= nr < grid.rows and 0 <= nc < grid.cols):
                        mismatches += 1
                    else:
                        # Check if neighbor has matching connection
                        neighbor_dirs = grid.get_connections(nr, nc)
                        if OPPOSITE[d] not in neighbor_dirs:
                            mismatches += 1
        
        # Count disconnected components (need at least (components-1) connections to merge)
        visited = set()
        components = 0
        
        for r in range(grid.rows):
            for c in range(grid.cols):
                if (r, c) not in visited:
                    components += 1
                    stack = [(r, c)]
                    while stack:
                        cr, cc = stack.pop()
                        if (cr, cc) in visited:
                            continue
                        visited.add((cr, cc))
                        
                        for d in grid.get_connections(cr, cc):
                            dr, dc = DIRS[d]
                            nr = cr + dr
                            nc = cc + dc
                            if (0 <= nr < grid.rows and 0 <= nc < grid.cols):
                                neighbor_dirs = grid.get_connections(nr, nc)
                                if OPPOSITE[d] in neighbor_dirs:
                                    stack.append((nr, nc))
        
        # Each mismatch requires at least 1 rotation, but we divide by 2 since
        # each connection involves 2 tiles. However, to be safe (admissible),
        # we use mismatches/2 rounded up, or just mismatches/2.
        # For components, we need at least (components-1) rotations to connect them.
        # Use max to ensure we don't underestimate
        mismatch_cost = mismatches / 2
        component_cost = max(0, components - 1)
        
        # Return ceiling of mismatch_cost + component_cost for a safe lower bound
        return int(mismatch_cost + component_cost + 0.5)
    
    def solve(self, grid):
        """
        A* search implementation.
        Uses priority queue with f(n) = g(n) + h(n)
        where g(n) is the number of rotations made and h(n) is the heuristic.
        """
        # Priority queue: (f_score, g_score, grid_state, tiebreaker)
        open_set = []
        tiebreaker = 0
        
        # Track visited states to avoid revisiting
        visited = set()
        
        # Initial state
        initial_g = 0
        initial_h = self.heuristic(grid)
        initial_f = initial_g + initial_h
        
        heapq.heappush(open_set, (initial_f, initial_g, tiebreaker, grid.deep_copy()))
        tiebreaker += 1
        
        while open_set:
            f_score, g_score, _, current = heapq.heappop(open_set)
            
            # Skip if already visited (backtrack)
            if current in visited:
                # Find the position that was changed to reach this state
                # We need to track which tile was modified, but since we don't have parent info,
                # we'll use a generic backtrack step
                self.steps.append((current.deep_copy(), None, "backtrack", None))
                continue
            
            visited.add(current)
            self.nodes_expanded += 1
            
            # Check if goal
            if current.is_goal():
                self.steps.append((current.deep_copy(), None, "done", None))
                return current
            
            # Generate successors
            for r in range(current.rows):
                for c in range(current.cols):
                    # Try all 4 rotations for this tile
                    for rot in range(4):
                        successor = current.deep_copy()
                        successor.grid[r][c].rotation = rot
                        
                        # Track try step
                        self.steps.append((successor.deep_copy(), (r, c), "try", rot))
                        
                        # Skip if already visited (backtrack)
                        if successor in visited:
                            self.steps.append((successor.deep_copy(), (r, c), "backtrack", None))
                            continue
                        
                        # Pruning: check if this rotation is valid (backtrack if invalid)
                        if not successor.partial_valid(r, c):
                            self.steps.append((successor.deep_copy(), (r, c), "backtrack", None))
                            continue
                        
                        # Calculate new scores
                        new_g = g_score + 1  # Cost of one rotation
                        new_h = self.heuristic(successor)
                        new_f = new_g + new_h
                        
                        heapq.heappush(open_set, (new_f, new_g, tiebreaker, successor))
                        tiebreaker += 1
        
        return None



