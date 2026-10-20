"""Classic Snake game — standard library only (tkinter).

The rules live in `Game`, which has no GUI dependencies and can be tested
headlessly. `SnakeApp` renders a `Game` with tkinter and handles input.

Run:  python snake.py
"""

import random
import sys

# --- Configuration -----------------------------------------------------------

CELL_SIZE = 20
GRID_SIZE = 20
TICK_MS = 120

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# --- Colours -----------------------------------------------------------------

BG = "#101418"
SNAKE_HEAD = "#4ade80"
SNAKE_BODY = "#22c55e"
FOOD = "#ef4444"
TEXT = "#e5e7eb"


# --- Game logic --------------------------------------------------------------


class Game:
    """Grid based snake: grow by eating, die on walls and on yourself."""

    def __init__(self, grid=GRID_SIZE):
        self.grid = grid
        self.reset()

    def reset(self):
        self.snake = [(self.grid // 2, self.grid // 2)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.paused = False
        self.game_over = False
        self.won = False
        self.food = self._spawn_food()

    def _spawn_food(self):
        """Pick a random empty cell, or None when the board is full."""
        free = [
            (x, y)
            for x in range(self.grid)
            for y in range(self.grid)
            if (x, y) not in self.snake
        ]
        return random.choice(free) if free else None

    def set_direction(self, direction):
        """Queue a new heading; ignores 180 degree turns."""
        if self.game_over:
            return
        if direction == (-self.direction[0], -self.direction[1]):
            return
        self.next_direction = direction

    def toggle_pause(self):
        if not self.game_over:
            self.paused = not self.paused

    def step(self):
        """Advance one tick. Returns 'ate', 'dead', 'won' or None."""
        if self.game_over or self.paused:
            return None

        self.direction = self.next_direction
        dx, dy = self.direction
        hx, hy = self.snake[0]
        head = (hx + dx, hy + dy)

        x, y = head
        if not (0 <= x < self.grid and 0 <= y < self.grid):
            self.game_over = True
            return "dead"
        if head in self.snake[:-1]:
            self.game_over = True
            return "dead"

        self.snake.insert(0, head)
        if head == self.food:
            self.score += 1
            self.food = self._spawn_food()
            if self.food is None:
                self.won = True
                self.game_over = True
                return "won"
            return "ate"

        self.snake.pop()
        return None


# --- User interface ----------------------------------------------------------


class SnakeApp:
    """Tkinter front end for `Game`."""

    KEY_MAP = {
        "up": UP,
        "w": UP,
        "down": DOWN,
        "s": DOWN,
        "left": LEFT,
        "a": LEFT,
        "right": RIGHT,
        "d": RIGHT,
    }

    def __init__(self, root, game=None):
        import tkinter as tk

        self.tk = tk
        self.root = root
        self.game = game or Game()
        self.high_score = 0
        self.board = CELL_SIZE * self.game.grid

        root.title("Snake")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.canvas = tk.Canvas(
            root, width=self.board, height=self.board, bg=BG, highlightthickness=0
        )
        self.canvas.pack()

        self.score_var = tk.StringVar()
        tk.Label(
            root, textvariable=self.score_var, bg=BG, fg=TEXT, font=("Consolas", 12)
        ).pack(pady=4)

        self.draw()
        root.bind("<KeyPress>", self.on_key)
        self.root.after(TICK_MS, self.tick)

    # -- input ---------------------------------------------------------------

    def on_key(self, event):
        key = event.keysym.lower()

        if key in self.KEY_MAP:
            self.game.set_direction(self.KEY_MAP[key])
        elif key == "p":
            self.game.toggle_pause()
        elif key == "r":
            self.game.reset()
        elif key in ("escape", "q"):
            self.root.destroy()

    # -- loop ----------------------------------------------------------------

    def tick(self):
        event = self.game.step()
        if event == "dead":
            self.high_score = max(self.high_score, self.game.score)
        self.draw()
        self.root.after(TICK_MS, self.tick)

    # -- drawing -------------------------------------------------------------

    def draw(self):
        canvas = self.canvas
        canvas.delete("all")

        if self.game.food is not None:
            fx, fy = self.game.food
            canvas.create_rectangle(
                fx * CELL_SIZE,
                fy * CELL_SIZE,
                (fx + 1) * CELL_SIZE,
                (fy + 1) * CELL_SIZE,
                fill=FOOD,
                outline="",
            )

        for index, (sx, sy) in enumerate(self.game.snake):
            canvas.create_rectangle(
                sx * CELL_SIZE,
                sy * CELL_SIZE,
                (sx + 1) * CELL_SIZE,
                (sy + 1) * CELL_SIZE,
                fill=SNAKE_HEAD if index == 0 else SNAKE_BODY,
                outline="",
            )

        self.high_score = max(self.high_score, self.game.score)
        self.score_var.set(
            f"Score: {self.game.score}   High: {self.high_score}"
            + ("   [PAUSED]" if self.game.paused else "")
        )

        if self.game.game_over:
            message = "You win!" if self.game.won else "Game over - press R"
            canvas.create_rectangle(
                0, 0, self.board, self.board, fill=BG, stipple="gray25", outline=""
            )
            canvas.create_text(
                self.board / 2,
                self.board / 2,
                text=message,
                fill=TEXT,
                font=("Consolas", 16, "bold"),
            )


def main():
    import tkinter as tk

    root = tk.Tk()
    SnakeApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
