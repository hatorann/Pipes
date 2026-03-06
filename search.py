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



