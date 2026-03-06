# A* Search Algorithm for Pipe Puzzle - Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [What is A* Search?](#what-is-a-search)
3. [Problem Domain: Pipe Puzzle](#problem-domain-pipe-puzzle)
4. [A* Search Formula](#a-search-formula)
5. [Step-by-Step Algorithm Walkthrough](#step-by-step-algorithm-walkthrough)
6. [Heuristic Function Explained](#heuristic-function-explained)
7. [Data Structures](#data-structures)
8. [Backtrack Steps](#backtrack-steps)
9. [Example Execution](#example-execution)
10. [Complexity Analysis](#complexity-analysis)

---

## Overview

The A* (A-star) search algorithm is an informed search algorithm that finds the optimal path from a start state to a goal state. In this pipe puzzle solver, A* finds the minimum number of rotations needed to connect all pipes into a valid tree structure.

**Key Advantage**: Unlike DFS which explores blindly, A* uses a heuristic to guide the search toward the goal, making it much more efficient.

---

## What is A* Search?

A* is a best-first search algorithm that uses:
- **g(n)**: Actual cost from start to node n (number of rotations made)
- **h(n)**: Estimated cost from node n to goal (heuristic - must be admissible)
- **f(n) = g(n) + h(n)**: Total estimated cost

The algorithm always expands the node with the **lowest f(n)** first, ensuring optimal solutions when the heuristic is admissible (never overestimates).

---

## Problem Domain: Pipe Puzzle

### Goal State Requirements
A valid solution must satisfy:
1. **No leaks**: All pipe connections point to valid neighbors (within grid bounds)
2. **Mutual connections**: If tile A connects to tile B, tile B must connect back to A
3. **Fully connected**: All tiles form one connected component
4. **Tree structure**: Exactly `(rows × cols - 1)` edges (no cycles)

### Actions
- **Rotate any tile** by 0°, 90°, 180°, or 270° (rotations 0-3)
- Each rotation costs 1 unit

### State Space
- Each state is a grid configuration with specific rotations for each tile
- Total possible states: `4^(rows × cols)` (each tile can be in 4 rotation states)

---

## A* Search Formula

```
f(n) = g(n) + h(n)

Where:
- g(n) = number of rotations made to reach state n
- h(n) = heuristic estimate of rotations needed to reach goal
- f(n) = total estimated cost (priority for expansion)
```

**Example:**
- If we've made 2 rotations: `g(n) = 2`
- Heuristic estimates 3 more rotations needed: `h(n) = 3`
- Priority: `f(n) = 2 + 3 = 5`

---

## Step-by-Step Algorithm Walkthrough

### Initialization (Lines 114-127)

```python
# 1. Create empty priority queue (min-heap)
open_set = []

# 2. Create visited set to avoid revisiting states
visited = set()

# 3. Calculate initial state scores
initial_g = 0                    # No rotations made yet
initial_h = self.heuristic(grid) # Estimate remaining rotations
initial_f = initial_g + initial_h # Total priority

# 4. Push initial state to queue
heapq.heappush(open_set, (initial_f, initial_g, tiebreaker, grid.deep_copy()))
```

**What happens:**
- The starting puzzle configuration is added to the priority queue
- The tiebreaker ensures deterministic ordering when f-scores are equal

---

### Main Loop (Lines 129-177)

#### Step 1: Pop Best Node (Line 130)
```python
f_score, g_score, _, current = heapq.heappop(open_set)
```
- Removes the node with **lowest f(n)** from the priority queue
- This is the most promising state to explore next

#### Step 2: Check if Already Visited (Lines 132-138)
```python
if current in visited:
    self.steps.append((current.deep_copy(), None, "backtrack", None))
    continue
```
- **Why?** The same state might be reached via different paths
- If already explored, skip it (backtrack step recorded)
- This prevents infinite loops and redundant work

#### Step 3: Mark as Visited (Line 140)
```python
visited.add(current)
self.nodes_expanded += 1
```
- Mark this state as explored
- Increment the node counter

#### Step 4: Check Goal (Lines 143-146)
```python
if current.is_goal():
    self.steps.append((current.deep_copy(), None, "done", None))
    return current
```
- If this state satisfies all goal conditions → **Solution found!**
- Return the solved grid

#### Step 5: Generate Successors (Lines 148-175)

For each tile position `(r, c)` in the grid:
```python
for r in range(current.rows):
    for c in range(current.cols):
```

For each possible rotation (0, 1, 2, 3):
```python
for rot in range(4):
    # Create new state by rotating tile at (r, c)
    successor = current.deep_copy()
    successor.grid[r][c].rotation = rot
```

**What this does:**
- Creates a new state by rotating one tile
- Generates up to `4 × (rows × cols)` successors per node

#### Step 6: Track "Try" Step (Line 157)
```python
self.steps.append((successor.deep_copy(), (r, c), "try", rot))
```
- Records that we're attempting this rotation
- Used for visualization

#### Step 7: Skip if Already Visited (Lines 159-162)
```python
if successor in visited:
    self.steps.append((successor.deep_copy(), (r, c), "backtrack", None))
    continue
```
- If we've seen this state before, skip it (backtrack)

#### Step 8: Prune Invalid States (Lines 164-167)
```python
if not successor.partial_valid(r, c):
    self.steps.append((successor.deep_copy(), (r, c), "backtrack", None))
    continue
```
- **Partial validation**: Checks if the rotated tile creates leaks or invalid connections
- Invalid states are skipped (backtrack)

#### Step 9: Calculate Scores and Add to Queue (Lines 169-175)
```python
new_g = g_score + 1              # One more rotation made
new_h = self.heuristic(successor) # Estimate remaining rotations
new_f = new_g + new_h            # Total priority

heapq.heappush(open_set, (new_f, new_g, tiebreaker, successor))
```
- Calculate new f-score
- Add to priority queue for future exploration
- Lower f-score = higher priority

---

## Heuristic Function Explained

The heuristic `h(n)` estimates the minimum number of rotations needed to reach the goal. It must be **admissible** (never overestimate).

### Part 1: Count Mismatched Connections (Lines 52-71)

```python
mismatches = 0
for r in range(grid.rows):
    for c in range(grid.cols):
        dirs = grid.get_connections(r, c)
        for d in dirs:
            # Check if connection goes out of bounds (leak)
            if not (0 <= nr < grid.rows and 0 <= nc < grid.cols):
                mismatches += 1
            # Check if neighbor doesn't connect back
            elif OPPOSITE[d] not in neighbor_dirs:
                mismatches += 1
```

**What it counts:**
- **Leaks**: Connections pointing outside the grid
- **Mismatches**: Connections where neighbor doesn't connect back

**Example:**
```
Tile A connects RIGHT → Tile B
But Tile B doesn't connect LEFT ←
This is a mismatch (needs at least 1 rotation to fix)
```

### Part 2: Count Disconnected Components (Lines 73-95)

```python
components = 0
visited = set()
# Use DFS to find all connected components
for r in range(grid.rows):
    for c in range(grid.cols):
        if (r, c) not in visited:
            components += 1
            # DFS to mark all tiles in this component
            # ...
```

**What it counts:**
- Number of separate pipe networks
- Goal: 1 component (all tiles connected)
- Need at least `(components - 1)` rotations to merge them

**Example:**
```
Grid has 3 disconnected pipe groups
Need at least 2 rotations to connect them into 1
```

### Part 3: Calculate Heuristic Value (Lines 97-106)

```python
mismatch_cost = mismatches / 2      # Each mismatch involves 2 tiles
component_cost = max(0, components - 1)
return int(mismatch_cost + component_cost + 0.5)
```

**Why divide by 2?**
- Each connection involves 2 tiles
- One rotation can fix both sides of a mismatch
- Dividing by 2 gives a conservative estimate

**Final heuristic:**
- `mismatch_cost`: Estimated rotations to fix connection issues
- `component_cost`: Estimated rotations to merge components
- Sum provides a lower bound on remaining work

---

## Data Structures

### 1. Priority Queue (Min-Heap)
```python
open_set = []  # Stores: (f_score, g_score, tiebreaker, grid_state)
```
- **Purpose**: Always get the node with lowest f(n) first
- **Operations**: `heappush()` (O(log n)), `heappop()` (O(log n))
- **Ordering**: By f_score, then g_score, then tiebreaker

### 2. Visited Set
```python
visited = set()  # Stores grid states (using hash of rotation tuple)
```
- **Purpose**: Avoid revisiting the same state
- **Lookup**: O(1) average case
- **Storage**: Hash of rotation tuple for each tile

### 3. Steps List
```python
self.steps = []  # Stores: (grid_copy, position, action, rotation)
```
- **Purpose**: Track search process for visualization
- **Actions**: "try", "backtrack", "done"
- **Used by**: UI visualization system

---

## Backtrack Steps

Backtrack steps are recorded when A* skips exploring a state. Three scenarios:

### 1. Already Visited (Line 137)
```python
if current in visited:
    self.steps.append((current.deep_copy(), None, "backtrack", None))
```
- **When**: Same state reached via different path
- **Why**: Already explored, no need to revisit

### 2. Successor Already Visited (Line 161)
```python
if successor in visited:
    self.steps.append((successor.deep_copy(), (r, c), "backtrack", None))
```
- **When**: Generated successor was already explored
- **Why**: Avoid duplicate work

### 3. Invalid State (Line 166)
```python
if not successor.partial_valid(r, c):
    self.steps.append((successor.deep_copy(), (r, c), "backtrack", None))
```
- **When**: Rotation creates leaks or invalid connections
- **Why**: Pruning invalid branches early

**Note**: Unlike DFS which backtracks up the recursion tree, A* backtracks by skipping states in the priority queue.

---

## Example Execution

### Initial State (2×2 Grid)
```
C3  C0    (Corner rotated 270°, Corner rotated 0°)
E1  E2    (End rotated 90°, End rotated 180°)
```

### Step 1: Initialize
- `g(initial) = 0`
- `h(initial) = 3` (example: 2 mismatches + 2 components - 1 = 3)
- `f(initial) = 0 + 3 = 3`
- Push to queue: `[(3, 0, 0, initial_state)]`

### Step 2: Pop Initial State
- Pop: `(3, 0, 0, initial_state)`
- Check goal: ❌ Not solved
- Mark visited: `visited = {initial_state}`

### Step 3: Generate Successors
For each tile and rotation:
- Try rotating (0,0) to rotation 0, 1, 2, 3
- Try rotating (0,1) to rotation 0, 1, 2, 3
- Try rotating (1,0) to rotation 0, 1, 2, 3
- Try rotating (1,1) to rotation 0, 1, 2, 3

For each valid successor:
- Calculate `new_g = 0 + 1 = 1`
- Calculate `new_h = heuristic(successor)`
- Calculate `new_f = new_g + new_h`
- Push to queue

### Step 4: Continue
- Pop next best state (lowest f-score)
- Repeat until goal found

### Step 5: Solution Found
- When `current.is_goal()` returns `True`
- Return the solved grid

---

## Complexity Analysis

### Time Complexity
- **Worst case**: O(b^d) where b = branching factor, d = depth
  - Branching factor: Up to `4 × (rows × cols)` successors per node
  - Depth: Number of rotations needed (can be up to `rows × cols`)
- **With good heuristic**: Much better than DFS (explores fewer nodes)
- **Best case**: O(1) if initial state is goal

### Space Complexity
- **Visited set**: O(4^(rows×cols)) worst case (all possible states)
- **Priority queue**: O(b^d) in worst case
- **Steps list**: O(n) where n = number of steps taken

### Why A* is Efficient
1. **Heuristic guidance**: Explores promising paths first
2. **Early pruning**: Skips invalid states immediately
3. **Visited tracking**: Avoids redundant exploration
4. **Optimal**: Guarantees minimum rotations when heuristic is admissible

---

## Key Differences from DFS

| Aspect | DFS | A* |
|--------|-----|-----|
| **Exploration** | Depth-first (blind) | Best-first (guided) |
| **Ordering** | LIFO (stack) | Priority queue (f-score) |
| **Optimality** | Not guaranteed | Guaranteed (with admissible heuristic) |
| **Efficiency** | Explores many nodes | Explores fewer nodes |
| **Backtrack** | Recursive backtracking | Skips states in queue |

---

## Summary

A* search for pipe puzzles:
1. Uses a priority queue to explore most promising states first
2. Estimates remaining work with an admissible heuristic
3. Tracks visited states to avoid redundancy
4. Prunes invalid states early
5. Guarantees optimal solution (minimum rotations)
6. Records steps for visualization (try, backtrack, done)

The algorithm efficiently finds the solution by balancing:
- **Exploration** (trying new states)
- **Exploitation** (focusing on promising paths via heuristic)

---

## References

- A* algorithm: [Wikipedia - A* search algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)
- Admissible heuristics: Must never overestimate the true cost
- Implementation: See `search.py` lines 42-177
