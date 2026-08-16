import asyncio
import random
import pygame




SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
OCEAN_BG = (100, 200, 255)

PADDLE_WIDTH = 200
PADDLE_HEIGHT = 10
PADDLE_ACCELERATION = 2
MAX_SPEED = 15

BALL_RADIUS = 10
BALL_SPEED_INCREMENT = 0.01

BLOCK_WIDTH = 40
BLOCK_HEIGHT = 15
BLOCK_GAP = 10

BLOCK_PATTERN = [
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
]

EYE_POSITIONS = {(5, 3)}

BLOCK_OFFSET_X = (
    SCREEN_WIDTH
    - (BLOCK_WIDTH + BLOCK_GAP) * len(BLOCK_PATTERN[0])
) // 2
BLOCK_OFFSET_Y = 35




def get_block_color(row_index, max_rows):
    top_color = (0, 50, 160)
    bottom_color = (120, 180, 255)

    ratio = row_index / max_rows

    r = top_color[0] + (bottom_color[0] - top_color[0]) * ratio
    g = top_color[1] + (bottom_color[1] - top_color[1]) * ratio
    b = top_color[2] + (bottom_color[2] - top_color[2]) * ratio

    return int(r), int(g), int(b)


def create_blocks():
    blocks = []

    for row_index, row in enumerate(BLOCK_PATTERN):
        block_row = []

        for col_index, block_on in enumerate(row):
            if block_on:
                block_x = (
                    col_index * (BLOCK_WIDTH + BLOCK_GAP)
                    + BLOCK_OFFSET_X
                )
                block_y = (
                    row_index * (BLOCK_HEIGHT + BLOCK_GAP)
                    + BLOCK_OFFSET_Y
                )

                block = pygame.Rect(
                    block_x,
                    block_y,
                    BLOCK_WIDTH,
                    BLOCK_HEIGHT,
                )

                block_row.append(block)

        blocks.append(block_row)

    return blocks



def draw_background(screen, bubbles):
    screen.fill(OCEAN_BG)

    for bubble in bubbles:
        bubble["y"] -= 1

        if bubble["y"] < 0:
            bubble["y"] = SCREEN_HEIGHT
            bubble["x"] = random.randint(0, SCREEN_WIDTH)
            bubble["r"] = random.randint(2, 5)

        pygame.draw.circle(
            screen,
            (200, 255, 255),
            (bubble["x"], bubble["y"]),
            bubble["r"],
        )


def draw_blocks(screen, blocks):
    for row_index, row in enumerate(blocks):
        for block in row:
            col_index = (
                block.left - BLOCK_OFFSET_X
            ) // (BLOCK_WIDTH + BLOCK_GAP)

            if (row_index, col_index) in EYE_POSITIONS:
                pygame.draw.rect(screen, (70, 70, 70), block)
                continue

            base_color = get_block_color(
                row_index,
                len(blocks),
            )

            pygame.draw.rect(screen, base_color, block)

           
            dot_color = (
                min(base_color[0] + 30, 255),
                min(base_color[1] + 30, 255),
                min(base_color[2] + 30, 255),
            )

            dot_radius = 4

            for i in range(2):
                for j in range(4):
                    dot_x = (
                        block.left
                        + (j + 0.5) * BLOCK_WIDTH / 4
                    )
                    dot_y = (
                        block.top
                        + (i + 0.5) * BLOCK_HEIGHT / 2
                    )

                    pygame.draw.circle(
                        screen,
                        dot_color,
                        (int(dot_x), int(dot_y)),
                        dot_radius,
                    )


def draw_center_message(screen, font, lines, background=BLACK):
    screen.fill(background)

    total_height = sum(font.size(line)[1] for line in lines)
    spacing = 8
    total_height += spacing * max(0, len(lines) - 1)

    y = SCREEN_HEIGHT // 2 - total_height // 2

    for line in lines:
        surface = font.render(line, True, WHITE)
        x = SCREEN_WIDTH // 2 - surface.get_width() // 2
        screen.blit(surface, (x, y))
        y += surface.get_height() + spacing

    pygame.display.flip()




async def countdown(screen, font):
    for count in range(3, 0, -1):
        draw_center_message(
            screen,
            font,
            ["Stage 4", f"Starting in {count}"],
        )

        await asyncio.sleep(1)




async def game_loop(screen, font):
    paddle = pygame.Rect(
        SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2,
        SCREEN_HEIGHT - 30,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
    )

    ball = pygame.Rect(
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2,
        BALL_RADIUS * 2,
        BALL_RADIUS * 2,
    )

    ball_speed_x = 5
    ball_speed_y = 5

    paddle_speed = 5
    left_passed_time = 0
    right_passed_time = 0

    score = 0
    blocks = create_blocks()

    bubbles = [
        {
            "x": random.randint(0, SCREEN_WIDTH),
            "y": random.randint(0, SCREEN_HEIGHT),
            "r": random.randint(2, 5),
        }
        for _ in range(30)
    ]

    clock = pygame.time.Clock()

    paused = False
    running = True

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

        
        if paused:
            draw_center_message(
                screen,
                font,
                ["PAUSED", "Press P to Resume"],
            )

            await asyncio.sleep(0)
            continue

       
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            left_passed_time += 1
            right_passed_time = 0

            paddle_speed = min(
                10 + PADDLE_ACCELERATION * left_passed_time,
                MAX_SPEED,
            )

            if paddle.left > 0:
                paddle.left -= paddle_speed

        elif keys[pygame.K_RIGHT]:
            right_passed_time += 1
            left_passed_time = 0

            paddle_speed = min(
                10 + PADDLE_ACCELERATION * right_passed_time,
                MAX_SPEED,
            )

            if paddle.right < SCREEN_WIDTH:
                paddle.right += paddle_speed

        else:
            left_passed_time = 0
            right_passed_time = 0
            paddle_speed = 5

       
        ball.left += int(ball_speed_x)
        ball.top += int(ball_speed_y)

        
        if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
            ball_speed_x = -ball_speed_x * (
                1 + BALL_SPEED_INCREMENT
            )

        if ball.top <= 0:
            ball_speed_y = -ball_speed_y * (
                1 + BALL_SPEED_INCREMENT
            )

        if ball.bottom >= SCREEN_HEIGHT:
            return "game_over", score

        
        if ball.colliderect(paddle):
            hit_pos = (
                (ball.left + ball.right) / 2
                - (paddle.left + paddle.right) / 2
            )

            ball_speed_x = hit_pos * 0.3
            ball_speed_y = -ball_speed_y

            ball_speed_x *= 1.05
            ball_speed_y *= 1.05

            ball_speed_x = max(
                -MAX_SPEED,
                min(MAX_SPEED, ball_speed_x),
            )

            ball_speed_y = max(
                -MAX_SPEED,
                min(MAX_SPEED, ball_speed_y),
            )

       
        block_hit = False

        for row in blocks:
            for block in row:
                if ball.colliderect(block):
                    ball_speed_y = -ball_speed_y * (
                        1 + BALL_SPEED_INCREMENT
                    )

                    row.remove(block)
                    score += 100
                    block_hit = True
                    break

            if block_hit:
                break

        
        draw_background(screen, bubbles)

        pygame.draw.rect(screen, BLUE, paddle)
        pygame.draw.ellipse(screen, WHITE, ball)

        draw_blocks(screen, blocks)

        score_text = font.render(
            f"Score: {score}",
            True,
            WHITE,
        )

        screen.blit(score_text, (10, 10))

        pygame.display.flip()

        
        if all(len(row) == 0 for row in blocks):
            return "clear", score

        clock.tick(FPS)

        
        await asyncio.sleep(0)




async def game_over_screen(screen, font, score):
    while True:
        draw_center_message(
            screen,
            font,
            [
                "GAME OVER",
                f"Score: {score}",
                "R: Retry   ESC: Exit",
            ],
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"

                if event.key == pygame.K_ESCAPE:
                    return "quit"

        await asyncio.sleep(0)




async def clear_screen(screen, font, score):
    while True:
        draw_center_message(
            screen,
            font,
            [
                "STAGE 4 CLEAR!",
                f"Score: {score}",
                "R: Retry   ESC: Exit",
            ],
            background=(102, 205, 170),
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"

                if event.key == pygame.K_ESCAPE:
                    return "quit"
        await asyncio.sleep(0)



async def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    pygame.display.set_caption(
        "Block Breakerz - Stage 4"
    )

    font = pygame.font.Font(None, 36)

    while True:
        await countdown(screen, font)

        result = await game_loop(screen, font)

        if result == "quit":
            break

        state, score = result

        if state == "clear":
            action = await clear_screen(
                screen,
                font,
                score,
            )

        else:
            action = await game_over_screen(
                screen,
                font,
                score,
            )

        if action == "quit":
            break

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
