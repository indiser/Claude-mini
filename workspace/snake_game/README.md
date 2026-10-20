# Snake

Classic grid-based Snake game in Python, using only the standard library
(`tkinter`) — no third-party packages to install.

## Run

```bash
cd snake_game
python snake.py
```

## Controls

| Key           | Action                     |
| ------------- | -------------------------- |
| Arrow keys    | Steer (WASD works too)     |
| `P`           | Pause / resume             |
| `R`           | Restart                    |
| `Q` / `Esc`   | Quit                       |

Eat the red food to grow. Hitting a wall or your own tail ends the game.

## Layout

- `snake.py` — `Game` holds the rules (headless, unit-testable),
  `SnakeApp` renders it with tkinter.
- `test_snake.py` — logic tests, no GUI required.
