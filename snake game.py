import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import random
import sys

pygame.init()

try:
    pygame.mixer.init()
except pygame.error:
    pass


CELL, W, H, TOP = 20, 50, 30, 40
SW, SH = W * CELL, H * CELL + TOP

WHITE = (240, 240, 240)
GREEN = (0, 200, 90)
DARK_GREEN = (0, 140, 60)
YELLOW = (240, 200, 60)
RED = (220, 40, 40)
PURPLE = (160, 40, 220)
GRAY = (90, 90, 100)
BG = (25, 25, 35)


screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()


large = pygame.font.SysFont("arial", 48, True)
medium = pygame.font.SysFont("arial", 30, True)
small = pygame.font.SysFont("arial", 20)


directions = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_w: (0, -1),
    pygame.K_s: (0, 1),
    pygame.K_a: (-1, 0),
    pygame.K_d: (1, 0)
}


sound_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sounds"
)

sounds = {}

for n, f in {
    "eat": "eat.mp3",
    "collision": "slash.mp3",
    "game_over": "game over.mp3"
}.items():
    try:
        sounds[n] = pygame.mixer.Sound(
            os.path.join(sound_dir, f)
        )
        sounds[n].set_volume(1)
    except (pygame.error, FileNotFoundError):
        sounds[n] = None


def play_sound(n):
    if sounds.get(n):
        sounds[n].play()


class Node:
    def __init__(self, x, y, next=None):
        self.x = x
        self.y = y
        self.next = next


class Snake:
    def __init__(self, x=W // 2, y=H // 2):
        self.head = self.tail = Node(x, y)
        self.length = 1

    def positions(self):
        n = self.head

        while n:
            yield n.x, n.y
            n = n.next

    def contains(self, x, y):
        n = self.head

        while n:
            if (n.x, n.y) == (x, y):
                return True

            n = n.next

        return False

    def find(self, x, y):
        n = self.head
        i = 0

        while n:
            if (n.x, n.y) == (x, y):
                return i

            n = n.next
            i += 1

        return -1

    def move(self, d, grow=False):
        self.head = Node(
            self.head.x + d[0],
            self.head.y + d[1],
            self.head
        )

        self.length += 1

        if not grow:
            n = self.head

            while n.next != self.tail:
                n = n.next

            n.next = None
            self.tail = n
            self.length -= 1

    def cut(self, index):
        if index <= 0:
            return

        n = self.head

        for _ in range(index - 1):
            n = n.next

        n.next = None
        self.tail = n
        self.length = index


def spawn(snake, blocked=None):
    blocked = blocked or set()

    while True:
        p = (
            random.randint(1, W - 2),
            random.randint(1, H - 2)
        )

        if not snake.contains(*p) and p not in blocked:
            return p


def draw_button(r, text, color):
    pygame.draw.rect(
        screen,
        (35, 35, 45),
        r,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        WHITE if r.collidepoint(pygame.mouse.get_pos()) else GRAY,
        r,
        3,
        border_radius=12
    )

    t = medium.render(text, True, color)
    screen.blit(
        t,
        t.get_rect(center=r.center)
    )


def draw_border():
    for x in range(0, SW, 40):
        for y in (TOP, SH - 20):
            r = pygame.Rect(
                x,
                y,
                40,
                20
            )

            pygame.draw.rect(
                screen,
                RED,
                r
            )

            pygame.draw.rect(
                screen,
                WHITE,
                r,
                2
            )

    for y in range(TOP + 20, SH - 20, 20):
        for x in (0, SW - 20):
            r = pygame.Rect(
                x,
                y,
                20,
                20
            )

            pygame.draw.rect(
                screen,
                RED,
                r
            )

            pygame.draw.rect(
                screen,
                WHITE,
                r,
                2
            )


state = "home"
mode = "easy"

snake = Snake()
food = spawn(snake)
poison = None

direction = pending = (1, 0)

score = 0
timer = 0
poison_timer = 0

death_reason = ""


easy = pygame.Rect(0, 0, 220, 70)
easy.center = (SW // 2, 260)

hard = pygame.Rect(0, 0, 220, 70)
hard.center = (SW // 2, 350)


background = Snake()
background_direction = (1, 0)
background_timer = 0


def start_game(m):
    global state
    global mode
    global snake
    global food
    global poison
    global direction
    global pending
    global score
    global timer
    global poison_timer

    state = "play"
    mode = m
    snake = Snake()
    food = spawn(snake)
    poison = None

    direction = pending = (1, 0)

    score = 0
    timer = 0
    poison_timer = 0


running = True


while running:
    dt = clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if state == "home":

                if event.key in (pygame.K_1, pygame.K_e):
                    start_game("easy")

                elif event.key in (pygame.K_2, pygame.K_h):
                    start_game("hard")

            elif state == "play":

                if event.key in directions:
                    d = directions[event.key]

                    if d != (-direction[0], -direction[1]):
                        pending = d

                elif event.key == pygame.K_ESCAPE:
                    state = "home"

            elif state == "over":

                if event.key == pygame.K_r:
                    start_game(mode)

                elif event.key in (pygame.K_h, pygame.K_ESCAPE):
                    state = "home"

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if state == "home":

                if easy.collidepoint(event.pos):
                    start_game("easy")

                elif hard.collidepoint(event.pos):
                    start_game("hard")

            elif state == "over":

                if restart.collidepoint(event.pos):
                    start_game(mode)

                elif home.collidepoint(event.pos):
                    state = "home"


    # HOME
    if state == "home":

        background_timer += dt

        if background_timer >= 120:
            background_timer = 0

            if random.random() < 0.25:
                choices = [
                    d
                    for d in directions.values()
                    if d != (
                        -background_direction[0],
                        -background_direction[1]
                    )
                ]

                background_direction = random.choice(choices)

            background.move(
                background_direction,
                True
            )

            if background.length > 8:
                n = background.head

                while n.next != background.tail:
                    n = n.next

                n.next = None
                background.tail = n
                background.length -= 1

            if not (
                1 <= background.head.x < W - 1
                and 1 <= background.head.y < H - 1
            ):
                background = Snake()


    # GAME
    elif state == "play":

        timer += dt
        now = pygame.time.get_ticks()

        if mode == "hard":

            poison_timer += dt

            if poison and now - poison[2] >= 5000:
                poison = None

            elif not poison and poison_timer >= 15000:
                p = spawn(
                    snake,
                    {food}
                )

                poison = (*p, now)
                poison_timer = 0

        if timer >= 1000 // (6 if mode == "easy" else 10):

            timer = 0
            direction = pending

            nx = snake.head.x + direction[0]
            ny = snake.head.y + direction[1]

            if not (
                1 <= nx < W - 1
                and 1 <= ny < H - 1
            ):
                play_sound("game_over")

                death_reason = "You hit the wall!"
                state = "over"

            else:
                hit = snake.find(nx, ny)

                if hit != -1:

                    if mode == "easy":
                        play_sound("collision")

                        snake.cut(hit)
                        snake.move(direction)

                    else:
                        play_sound("game_over")

                        death_reason = "You ran into yourself!"
                        state = "over"

                elif poison and (nx, ny) == poison[:2]:
                    play_sound("game_over")

                    death_reason = "You ate the poison!"
                    state = "over"

                else:
                    grow = (nx, ny) == food

                    snake.move(
                        direction,
                        grow
                    )

                    if grow:
                        score += 1
                        play_sound("eat")

                        food = spawn(
                            snake,
                            {poison[:2]} if poison else set()
                        )


    screen.fill(BG)


    if state == "home":

        for i, (x, y) in enumerate(background.positions()):

            pygame.draw.circle(
                screen,
                YELLOW if i == 0 else DARK_GREEN,
                (
                    x * CELL + CELL // 2,
                    y * CELL + TOP + CELL // 2
                ),
                CELL // 2
            )

        t = large.render(
            "SNAKE GAME",
            True,
            WHITE
        )

        screen.blit(
            t,
            t.get_rect(center=(SW // 2, 100))
        )

        draw_button(
            easy,
            "EASY MODE",
            GREEN
        )

        draw_button(
            hard,
            "HARD MODE",
            RED
        )


    elif state == "play":

        pygame.draw.rect(
            screen,
            (30, 30, 40),
            (0, 0, SW, TOP)
        )

        screen.blit(
            small.render(
                f"Mode: {mode.upper()}",
                True,
                WHITE
            ),
            (30, 10)
        )

        screen.blit(
            small.render(
                f"Score: {score}",
                True,
                WHITE
            ),
            (SW - 130, 10)
        )


        # Circular snake + black eyes
        for i, (x, y) in enumerate(snake.positions()):

            cx = x * CELL + CELL // 2
            cy = y * CELL + TOP + CELL // 2

            pygame.draw.circle(
                screen,
                YELLOW if i == 0 else GREEN,
                (cx, cy),
                CELL // 2
            )

            if i == 0:

                pygame.draw.circle(
                    screen,
                    (20, 20, 20),
                    (cx - 5, cy - 5),
                    2
                )

                pygame.draw.circle(
                    screen,
                    (20, 20, 20),
                    (cx + 5, cy - 5),
                    2
                )


        pygame.draw.rect(
            screen,
            RED,
            (
                food[0] * CELL,
                food[1] * CELL + TOP,
                CELL,
                CELL
            ),
            border_radius=6
        )


        if poison:

            pygame.draw.rect(
                screen,
                PURPLE,
                (
                    poison[0] * CELL,
                    poison[1] * CELL + TOP,
                    CELL,
                    CELL
                ),
                border_radius=6
            )


        draw_border()


    else:

        t = large.render(
            "GAME OVER",
            True,
            RED
        )

        screen.blit(
            t,
            t.get_rect(center=(SW // 2, 120))
        )


        t = medium.render(
            death_reason,
            True,
            WHITE
        )

        screen.blit(
            t,
            t.get_rect(center=(SW // 2, 180))
        )


        t = medium.render(
            f"Final Score: {score}",
            True,
            YELLOW
        )

        screen.blit(
            t,
            t.get_rect(center=(SW // 2, 230))
        )


        restart = pygame.Rect(
            0,
            0,
            240,
            60
        )

        restart.center = (SW // 2, 320)


        home = pygame.Rect(
            0,
            0,
            240,
            60
        )

        home.center = (SW // 2, 400)


        draw_button(
            restart,
            "RESTART",
            GREEN
        )

        draw_button(
            home,
            "HOME",
            WHITE
        )


    pygame.display.flip()


pygame.quit()
sys.exit()