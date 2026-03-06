import pygame
import math
from puzzle import OPPOSITE, DIRS

# Enhanced color scheme
CELL = 120
PIPE_COLOR = (52, 152, 219)  # Modern blue
PIPE_COLOR_CONNECTED = (46, 204, 113)  # Green for connected
PIPE_COLOR_DISCONNECTED = (231, 76, 60)  # Red for disconnected
PIPE_COLOR_NEUTRAL = (149, 165, 166)  # Gray for neutral
BG_COLOR = (236, 240, 241)  # Light gray background
GRID_COLOR = (189, 195, 199)  # Grid lines
PANEL_COLOR = (52, 73, 94)  # Dark panel
TEXT_COLOR = (236, 240, 241)  # Light text
HIGHLIGHT_COLOR = (241, 196, 15)  # Yellow highlight
SHADOW_COLOR = (44, 62, 80)  # Dark shadow

def draw_pipe_enhanced(screen, pipe, x, y, cell_size, is_connected=False, is_valid=True, rotation_angle=0):
    """Draw a pipe with enhanced visuals, shadows, and connection status."""
    rect = pygame.Rect(x, y, cell_size, cell_size)
    
    # Background with gradient effect
    bg = (255, 255, 255)
    pygame.draw.rect(screen, bg, rect)
    
    # Shadow effect
    shadow_rect = pygame.Rect(x + 3, y + 3, cell_size, cell_size)
    pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect)
    pygame.draw.rect(screen, bg, rect)
    
    # Border
    border_color = PIPE_COLOR_CONNECTED if is_connected else (PIPE_COLOR_DISCONNECTED if not is_valid else GRID_COLOR)
    border_width = 3 if is_connected else 2
    pygame.draw.rect(screen, border_color, rect, border_width)
    
    center = (x + cell_size // 2, y + cell_size // 2)
    
    # Pipe thickness
    outer_thickness = cell_size // 6
    inner_thickness = cell_size // 12
    
    # Draw center circle with gradient effect
    pygame.draw.circle(screen, PIPE_COLOR if is_connected else PIPE_COLOR_NEUTRAL, center, outer_thickness // 2)
    pygame.draw.circle(screen, bg, center, inner_thickness // 2)
    
    # Get connections
    connections = pipe.get_connections()
    pipe_color = PIPE_COLOR_CONNECTED if is_connected else (PIPE_COLOR if is_valid else PIPE_COLOR_DISCONNECTED)
    
    # Draw connections with rotation animation
    for direction in connections:
        if direction == 0:  # up
            end = (center[0], y + 5)
        elif direction == 1:  # right
            end = (x + cell_size - 5, center[1])
        elif direction == 2:  # down
            end = (center[0], y + cell_size - 5)
        elif direction == 3:  # left
            end = (x + 5, center[1])
        else:
            continue
        
        # Outer pipe with rounded ends
        pygame.draw.line(screen, pipe_color, center, end, outer_thickness)
        pygame.draw.circle(screen, pipe_color, end, outer_thickness // 2)
        
        # Inner hollow
        pygame.draw.line(screen, bg, center, end, inner_thickness)
        pygame.draw.circle(screen, bg, end, inner_thickness // 2)


def get_connection_status(grid, r, c):
    """Check if a pipe is properly connected to its neighbors."""
    dirs = grid.get_connections(r, c)
    connected = True
    
    for d in dirs:
        dr, dc = DIRS[d]
        nr = r + dr
        nc = c + dc
        
        if not (0 <= nr < grid.rows and 0 <= nc < grid.cols):
            connected = False
            break
        
        neighbor_dirs = grid.get_connections(nr, nc)
        if OPPOSITE[d] not in neighbor_dirs:
            connected = False
            break
    
    return connected


def draw_connection_paths(screen, grid, start_x, start_y, cell_size):
    """Draw visual paths between connected pipes."""
    if not grid.is_goal():
        return
    
    # Draw connection lines between adjacent connected pipes
    for r in range(grid.rows):
        for c in range(grid.cols):
            center1 = (start_x + c * cell_size + cell_size // 2, 
                     start_y + r * cell_size + cell_size // 2)
            
            dirs = grid.get_connections(r, c)
            for d in dirs:
                dr, dc = DIRS[d]
                nr = r + dr
                nc = c + dc
                
                if 0 <= nr < grid.rows and 0 <= nc < grid.cols:
                    center2 = (start_x + nc * cell_size + cell_size // 2,
                              start_y + nr * cell_size + cell_size // 2)
                    
                    # Draw connection line
                    pygame.draw.line(screen, PIPE_COLOR_CONNECTED, center1, center2, 4)


def draw_grid_enhanced(screen, font, small_font, grid, highlight=None, status="", autoplay=False, 
                       nodes_expanded=0, solver_name="", is_solution=False):
    """Draw grid with enhanced visuals and information."""
    screen.fill(BG_COLOR)
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    grid_width = grid.cols * CELL
    grid_height = grid.rows * CELL
    
    # Center the grid
    start_x = (screen_width - grid_width) // 2
    start_y = 80
    
    # Draw title with grid size
    title = f"Pipe Puzzle Solver - {grid.rows}x{grid.cols}"
    title_text = font.render(title, True, PANEL_COLOR)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 20))
    
    # Draw connection paths first (behind pipes)
    if is_solution:
        draw_connection_paths(screen, grid, start_x, start_y, CELL)
    
    # Draw grid with connection status
    for r in range(grid.rows):
        for c in range(grid.cols):
            x = start_x + c * CELL
            y = start_y + r * CELL
            
            is_connected = get_connection_status(grid, r, c)
            is_valid = grid.partial_valid(r, c)
            
            draw_pipe_enhanced(screen, grid.grid[r][c], x, y, CELL, 
                             is_connected=is_connected, is_valid=is_valid)
    
    # Highlight current tile
    if highlight:
        r, c = highlight
        x = start_x + c * CELL
        y = start_y + r * CELL
        highlight_rect = pygame.Rect(x - 2, y - 2, CELL + 4, CELL + 4)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, highlight_rect, 4)
    
    # Draw solution indicator
    if is_solution and grid.is_goal():
        solution_text = font.render("✓ SOLUTION FOUND!", True, PIPE_COLOR_CONNECTED)
        screen.blit(solution_text, (screen_width // 2 - solution_text.get_width() // 2, 
                                   start_y + grid_height + 20))
    
    # Enhanced information panel
    panel_y = start_y + grid_height + 60
    panel_height = 140
    
    # Draw panel with gradient effect
    pygame.draw.rect(screen, PANEL_COLOR, (0, panel_y, screen_width, panel_height))
    pygame.draw.line(screen, TEXT_COLOR, (0, panel_y), (screen_width, panel_y), 2)
    
    # Status information
    y_offset = panel_y + 15
    
    # Solver and status
    if solver_name:
        solver_text = small_font.render(f"Solver: {solver_name}", True, TEXT_COLOR)
        screen.blit(solver_text, (20, y_offset))
    
    status_text = font.render(status, True, TEXT_COLOR)
    screen.blit(status_text, (screen_width // 2 - status_text.get_width() // 2, y_offset))
    
    # Statistics
    y_offset += 35
    stats_text = small_font.render(f"Nodes Expanded: {nodes_expanded:,}", True, TEXT_COLOR)
    screen.blit(stats_text, (20, y_offset))
    
    # Goal status
    goal_status = "Valid Solution" if grid.is_goal() else "In Progress"
    goal_color = PIPE_COLOR_CONNECTED if grid.is_goal() else TEXT_COLOR
    goal_text = small_font.render(f"Status: {goal_status}", True, goal_color)
    screen.blit(goal_text, (screen_width - goal_text.get_width() - 20, y_offset))
    
    # Controls
    y_offset += 30
    controls = [
        "→ Next Step",
        "← Previous Step", 
        "ENTER Toggle Autoplay",
        "SPACE Play/Pause",
        "ESC Quit"
    ]
    controls_text = "  |  ".join(controls)
    controls_surface = small_font.render(controls_text, True, TEXT_COLOR)
    screen.blit(controls_surface, (screen_width // 2 - controls_surface.get_width() // 2, y_offset))
    
    # Autoplay indicator
    y_offset += 25
    autoplay_text = small_font.render(f"Autoplay: {'ON' if autoplay else 'OFF'}", True, 
                                     PIPE_COLOR_CONNECTED if autoplay else PIPE_COLOR_NEUTRAL)
    screen.blit(autoplay_text, (screen_width // 2 - autoplay_text.get_width() // 2, y_offset))
    
    pygame.display.flip()


def visualize_solution(initial_grid, solver, solver_name="DFS"):
    """Visualize the solution process step by step."""
    pygame.init()
    
    width = 1400
    height = 900
    
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Pipe Puzzle Solver - {solver_name}")
    
    font = pygame.font.SysFont("Arial", 32, bold=True)
    small_font = pygame.font.SysFont("Arial", 18)
    
    clock = pygame.time.Clock()
    idx = 0
    autoplay = False
    paused = False
    
    # Suppress printing during solve
    import sys
    from io import StringIO
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    # Show solving message
    draw_grid_enhanced(
        screen, font, small_font, initial_grid,
        highlight=None,
        status=f"Solving with {solver_name}... Please wait...",
        autoplay=False,
        nodes_expanded=0,
        solver_name=solver_name,
        is_solution=False
    )
    pygame.display.flip()
    
    # Solve the puzzle
    solution = solver.solve(initial_grid)
    
    # Restore stdout
    sys.stdout = old_stdout
    
    if not solution:
        # Show no solution message
        draw_grid_enhanced(
            screen, font, small_font, initial_grid,
            highlight=None,
            status="No solution found.",
            autoplay=False,
            nodes_expanded=solver.nodes_expanded,
            solver_name=solver_name,
            is_solution=False
        )
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        return
    
    # Show solution with animation
    current_grid = initial_grid.deep_copy()
    target_grid = solution
    
    # Animate from initial to solution
    animation_steps = 60
    step_idx = 0
    
    running = True
    while running:
        clock.tick(60)
        
        # Animate transition
        if step_idx < animation_steps and not paused:
            # Interpolate between initial and solution
            alpha = step_idx / animation_steps
            # For simplicity, show solution after animation
            if step_idx == animation_steps - 1:
                current_grid = target_grid.deep_copy()
            step_idx += 1
        
        # Draw current state
        is_solution = (current_grid == target_grid)
        draw_grid_enhanced(
            screen, font, small_font, current_grid,
            highlight=None,
            status=f"Solution Visualization - {solver_name}",
            autoplay=autoplay,
            nodes_expanded=solver.nodes_expanded,
            solver_name=solver_name,
            is_solution=is_solution
        )
        
        # Autoplay logic
        if autoplay and not paused:
            pygame.time.delay(100)
            if step_idx >= animation_steps:
                # Show final solution
                current_grid = target_grid.deep_copy()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_RETURN:
                    autoplay = not autoplay
                
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                
                elif event.key == pygame.K_RIGHT:
                    if step_idx < animation_steps:
                        step_idx = min(step_idx + 5, animation_steps)
                
                elif event.key == pygame.K_LEFT:
                    if step_idx > 0:
                        step_idx = max(step_idx - 5, 0)
    
    pygame.quit()


def replay_steps(steps):
    """Replay search steps with enhanced visualization."""
    pygame.init()
    
    width = 1400
    height = 900
    
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pipe Puzzle Solver - Step Replay")
    
    font = pygame.font.SysFont("Arial", 32, bold=True)
    small_font = pygame.font.SysFont("Arial", 18)
    
    clock = pygame.time.Clock()
    idx = 0
    autoplay = False
    paused = False
    
    while True:
        clock.tick(60)
        
        if idx < len(steps):
            grid, pos, action, rot = steps[idx]
            
            # Build status text
            if action == "try":
                status = f"[{idx+1}/{len(steps)}] Trying rotation {rot}"
            elif action == "backtrack":
                status = f"[{idx+1}/{len(steps)}] Backtracking"
            elif action == "done":
                status = f"[{idx+1}/{len(steps)}] Solution Found!"
            else:
                status = f"[{idx+1}/{len(steps)}]"
            
            draw_grid_enhanced(
                screen, font, small_font, grid,
                highlight=pos,
                status=status,
                autoplay=autoplay,
                nodes_expanded=idx,
                is_solution=(action == "done")
            )
        
        # Autoplay logic
        if autoplay and not paused:
            pygame.time.delay(150)
            if idx < len(steps) - 1:
                idx += 1
            else:
                autoplay = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                
                if event.key == pygame.K_RIGHT:
                    if idx < len(steps) - 1:
                        idx += 1
                
                if event.key == pygame.K_LEFT:
                    if idx > 0:
                        idx -= 1
                
                if event.key == pygame.K_RETURN:
                    autoplay = not autoplay
                
                if event.key == pygame.K_SPACE:
                    paused = not paused
