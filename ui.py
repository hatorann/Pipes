import pygame

CELL = 100
MARGIN = 110
PIPE_COLOR = (30, 144, 255)
BG_COLOR = (245, 245, 245)
GRID_COLOR = (180, 180, 180)

def draw_pipe(screen, pipe, x, y):
    rect = pygame.Rect(x, y, CELL, CELL)

    bg = (250, 250, 250)

    pygame.draw.rect(screen, bg, rect)
    pygame.draw.rect(screen, GRID_COLOR, rect, 1)

    center = (x + CELL // 2, y + CELL // 2)

    outer_thickness = CELL // 8
    inner_thickness = CELL // 14

    pygame.draw.circle(screen, PIPE_COLOR, center, outer_thickness // 2)
    pygame.draw.circle(screen, bg, center, inner_thickness // 2)

    for direction in pipe.get_connections():

        if direction == 0:  # up
            end = (center[0], y)

        elif direction == 1:  # right
            end = (x + CELL, center[1])

        elif direction == 2:  # down
            end = (center[0], y + CELL)

        elif direction == 3:  # left
            end = (x, center[1])

        # outer pipe
        pygame.draw.line(
            screen,
            PIPE_COLOR,
            center,
            end,
            outer_thickness
        )

        # hollow inside
        pygame.draw.line(
            screen,
            bg,
            center,
            end,
            inner_thickness
        )


def draw_grid(screen, font, small_font, grid, highlight, status, autoplay):

    screen.fill(BG_COLOR)

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    grid_width = grid.cols * CELL
    grid_height = grid.rows * CELL

    start_x = (screen_width - grid_width) // 2

    start_y = (screen_height - grid_height - 120) // 2

    for r in range(grid.rows):
        for c in range(grid.cols):
            x = start_x + c * CELL
            y = start_y + r * CELL
            draw_pipe(screen, grid.grid[r][c], x, y)

    if highlight:
        r, c = highlight
        x = start_x + c * CELL
        y = start_y + r * CELL
        pygame.draw.rect(screen, (255, 200, 120),
                         (x, y, CELL, CELL), 4)

    # instruction panel
    panel_y = start_y + grid_height + 20

    pygame.draw.rect(screen, (230, 230, 230),
                     (0, panel_y,
                      screen_width, 100))

    instructions = "→ Next   ← Back   ENTER AutoPlay   ESC Quit"
    screen.blit(small_font.render(instructions, True, (50,50,50)),
                (screen_width//2 - 250, panel_y + 10))

    auto_text = f"Autoplay: {'ON' if autoplay else 'OFF'}"
    screen.blit(small_font.render(auto_text, True, (120,40,40)),
                (screen_width//2 - 250, panel_y + 35))

    screen.blit(font.render(status, True, (30,30,30)),
                (screen_width//2 - 250, panel_y + 60))

    pygame.display.flip()


def replay_steps(steps):

    pygame.init()

    width = 1080
    height = 800

    screen = pygame.display.set_mode((width , height ))
    pygame.display.set_caption("DFS Pipes Visualization")

    font = pygame.font.SysFont("consolas", 26, bold=True)
    small_font = pygame.font.SysFont("consolas", 18)

    clock = pygame.time.Clock()
    idx = 0
    autoplay = False

    while True:
        clock.tick(60)

        grid, pos, action, rot = steps[idx]

        # build status text
        if action == "try":
            status = f"[{idx+1}/{len(steps)}] TRY rotation {rot}"
        elif action == "backtrack":
            status = f"[{idx+1}/{len(steps)}] BACKTRACK"
        elif action == "done":
            status = f"[{idx+1}/{len(steps)}] DONE"
        else:
            status = f"[{idx+1}/{len(steps)}]"

        draw_grid(screen, font, small_font,
                  grid, pos, status, autoplay)

        # autoplay logic
        if autoplay:
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
                    if idx < len(steps)-1:
                        idx += 1

                if event.key == pygame.K_LEFT:
                    if idx > 0:
                        idx -= 1

                if event.key == pygame.K_RETURN:
                    autoplay = not autoplay