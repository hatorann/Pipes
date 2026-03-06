UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

PIPE_TYPES = {
    "C": [UP,RIGHT],        # Corner pipe
    "E": [UP],              # END pipe
    "T": [UP,RIGHT,LEFT],   # T pipe
    "S": [UP,DOWN],         # S pipe
}
# Direction rotation formula: new_direction = (old_direction + rotation) % 4

# Move utility
DIRS = {
    UP: (-1,0),
    DOWN: (1,0),
    LEFT: (0,-1),
    RIGHT: (0,1)
}

OPPOSITE = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT
}

VISUAL_MAP = {
    frozenset([UP, DOWN]): "│",
    frozenset([LEFT, RIGHT]): "─",
    frozenset([UP, RIGHT]): "└",
    frozenset([RIGHT, DOWN]): "┌",
    frozenset([DOWN, LEFT]): "┐",
    frozenset([LEFT, UP]): "┘",
    frozenset([UP]): "╵",
    frozenset([DOWN]): "╷",
    frozenset([LEFT]): "╴",
    frozenset([RIGHT]): "╶",
    frozenset([UP, RIGHT, LEFT]): "┴",
    frozenset([DOWN, RIGHT, LEFT]): "┬",
    frozenset([UP, DOWN, LEFT]): "┤",
    frozenset([UP, DOWN, RIGHT]): "├",
}

class Tile:
    def __init__(self, pipe_type, rotation = 0):
        self.pipe_type = pipe_type
        self.rotation = rotation % 4

    def get_connections(self):
        base_dirs = PIPE_TYPES[self.pipe_type]
        rotated_dirs = []

        for d in base_dirs:
            rotated_dirs.append((d + self.rotation)%4)
        return rotated_dirs


class Grid:
    def __init__(self, grid):
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.grid = grid
    def get_connections(self,r,c):
        return self.grid[r][c].get_connections()

    def _rotation_tuple(self):
        return tuple(self.grid[r][c].rotation
                     for r in range(self.rows)
                     for c in range(self.cols))

    def __eq__(self,other):
        return self._rotation_tuple() == other._rotation_tuple()
    
    def __hash__(self):
        return hash(self._rotation_tuple())
    
    def deep_copy(self):
        copy_grid = [[Tile(self.grid[r][c].pipe_type,self.grid[r][c].rotation)
                    for c in range(self.cols)]
                    for r in range(self.rows)]
        return Grid(copy_grid)
    
    def get_successors(self):
        successors = []

        for r in range(self.rows):
            for c in range(self.cols):

                new_state = self.deep_copy()
                new_state.grid[r][c].rotation = (
                    new_state.grid[r][c].rotation + 1
                ) % 4

                successors.append(new_state)

        return successors
    def partial_valid(self,r,c):
        dirs = self.get_connections(r,c)
        for d in dirs:
            dr,dc = DIRS[d]
            nr = r + dr
            nc = c + dc
            # Out of bound
            if not ( 0<=nr<self.rows and 0<=nc<self.cols):
                return False
            if nr < r or (nr == r and nc < c):
                neigh_dirs = self.get_connections(nr,nc)
                if OPPOSITE[d] not in neigh_dirs:
                    return False
        return True
    
    # Must satisfy these conditions:
    # * No leaks
    # * No cycles
    # * Fully connected (One component)
    # * Mutual connections (A -> B then B -> A)


    def is_goal(self):
        total_nodes = self.rows*self.cols
        edge_count = 0

        for r in range(self.rows):
            for c in range(self.cols):

                dirs = self.get_connections(r,c)
                
                for d in dirs:
                    dr = r + DIRS[d][0]
                    dc = c + DIRS[d][1]
                    # Out of bounds => leaks
                    if not( 0 <= dr <self.rows and  0 <= dc <self.cols):
                        return False
                    
                    neighbor_dirs = self.get_connections(dr,dc)
                    # Mutual connection
                    if OPPOSITE[d] not in neighbor_dirs:
                        return False
                    edge_count +=1

        real_edges = edge_count // 2

        # DFS
        visited = []
        stack = [(0,0)]
        while stack:
            r,c = stack.pop()
            
            if (r,c) in visited:
                continue
            
            visited.append((r,c))
            for d in self.get_connections(r,c):
                dr,dc = DIRS[d]
                nr = r + dr
                nc = c + dc
                stack.append((nr,nc))
        
        if len(visited) != total_nodes:
            return False
        
        if real_edges != total_nodes - 1:
            return False
        
        return True


    