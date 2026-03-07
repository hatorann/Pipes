import pygame

CELL = 100

BG_COLOR = (240, 242, 247)
GRID_COLOR = (210, 210, 210)

PIPE_BORDER = (0, 0, 0)
PIPE_GREEN = (40, 180, 99)

# thicker pipes
PIPE_WIDTH = CELL // 5

CELL_BG = (255, 255, 255)

ERROR_RED = (220, 70, 70)
HIGHLIGHT = (255, 180, 90)

PANEL_BG = (225, 228, 235)
TEXT = (40, 40, 40)


def is_connected(grid, r, c, direction):

    pipe = grid.grid[r][c]

    if direction not in pipe.get_connections():
        return False

    dr = [-1, 0, 1, 0]
    dc = [0, 1, 0, -1]

    nr = r + dr[direction]
    nc = c + dc[direction]

    if nr < 0 or nr >= grid.rows or nc < 0 or nc >= grid.cols:
        return False

    neighbor = grid.grid[nr][nc]

    return (direction + 2) % 4 in neighbor.get_connections()


def draw_pipe(screen, pipe, x, y, color=PIPE_BORDER):

    rect = pygame.Rect(x, y, CELL, CELL)

    pygame.draw.rect(screen, CELL_BG, rect, border_radius=6)
    pygame.draw.rect(screen, GRID_COLOR, rect, 1, border_radius=6)

    center = (x + CELL // 2, y + CELL // 2)

    pygame.draw.circle(screen, color, center, PIPE_WIDTH // 2, 3)

    for direction in pipe.get_connections():

        if direction == 0:
            end = (center[0], y)

        elif direction == 1:
            end = (x + CELL, center[1])

        elif direction == 2:
            end = (center[0], y + CELL)

        elif direction == 3:
            end = (x, center[1])

        pygame.draw.line(
            screen,
            color,
            center,
            end,
            PIPE_WIDTH
        )


def draw_grid(screen, font, small_font, grid, highlight, status, autoplay, step, total_steps):

    screen.fill(BG_COLOR)

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    grid_width = grid.cols * CELL
    grid_height = grid.rows * CELL

    start_x = (screen_width - grid_width) // 2
    start_y = (screen_height - grid_height - 140) // 2

    shadow_rect = pygame.Rect(
        start_x - 6,
        start_y - 6,
        grid_width + 12,
        grid_height + 12
    )

    pygame.draw.rect(screen, (200, 200, 200),
                     shadow_rect,
                     border_radius=8)

    for r in range(grid.rows):
        for c in range(grid.cols):

            x = start_x + c * CELL
            y = start_y + r * CELL

            pipe = grid.grid[r][c]

            color = PIPE_BORDER

            for d in pipe.get_connections():
                if is_connected(grid, r, c, d):
                    color = PIPE_GREEN
                    break

            draw_pipe(screen, pipe, x, y, color)

    if highlight:

        r, c = highlight

        x = start_x + c * CELL
        y = start_y + r * CELL

        color = HIGHLIGHT

        if "BACKTRACK" in status:
            color = ERROR_RED

        pygame.draw.rect(
            screen,
            color,
            (x - 2, y - 2, CELL + 4, CELL + 4),
            3,
            border_radius=6
        )

    panel_y = start_y + grid_height + 20

    panel_rect = pygame.Rect(
        40,
        panel_y,
        screen_width - 80,
        110
    )

    pygame.draw.rect(screen, PANEL_BG, panel_rect, border_radius=8)
    pygame.draw.rect(screen, GRID_COLOR, panel_rect, 1, border_radius=8)

    instructions = "→ Next   ← Back   ENTER AutoPlay   ESC Quit"

    inst_surface = small_font.render(instructions, True, TEXT)

    screen.blit(
        inst_surface,
        (
            panel_rect.centerx - inst_surface.get_width() // 2,
            panel_y + 10
        )
    )

    auto_text = f"Autoplay: {'ON' if autoplay else 'OFF'}"

    auto_surface = small_font.render(auto_text, True, TEXT)

    screen.blit(
        auto_surface,
        (
            panel_rect.centerx - auto_surface.get_width() // 2,
            panel_y + 35
        )
    )

    step_text = f"Step: {step} / {total_steps}"

    step_surface = small_font.render(step_text, True, TEXT)

    screen.blit(
        step_surface,
        (
            panel_rect.centerx - step_surface.get_width() // 2,
            panel_y + 60
        )
    )

    status_surface = font.render(status, True, TEXT)

    screen.blit(
        status_surface,
        (
            panel_rect.centerx - status_surface.get_width() // 2,
            panel_y + 80
        )
    )

    pygame.display.flip()


def replay_steps(steps):

    pygame.init()

    width = 1000
    height = 850

    screen = pygame.display.set_mode((width, height))

    pygame.display.set_caption("DFS Pipes Visualization")

    font = pygame.font.SysFont("consolas", 26, bold=True)
    small_font = pygame.font.SysFont("consolas", 18)

    clock = pygame.time.Clock()

    idx = 0
    autoplay = False

    total_steps = len(steps)

    while True:

        clock.tick(60)

        grid, pos, action, rot = steps[idx]

        if action == "try":
            status = f"TRY rotation {rot}"

        elif action == "backtrack":
            status = f"BACKTRACK"

        elif action == "done":
            status = f"SOLVED"

        else:
            status = ""

        draw_grid(
            screen,
            font,
            small_font,
            grid,
            pos,
            status,
            autoplay,
            idx + 1,
            total_steps
        )

        if autoplay:

            pygame.time.delay(150)

            if idx < total_steps - 1:
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
                    if idx < total_steps - 1:
                        idx += 1

                if event.key == pygame.K_LEFT:
                    if idx > 0:
                        idx -= 1

                if event.key == pygame.K_RETURN:
                    autoplay = not autoplay