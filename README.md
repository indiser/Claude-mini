# 🤖 Claude Mini — A Tiny AI Agent That Got Bored and Made a Snake Game

> *"What if we built a mini Claude... but on a budget?"*
> — This project, probably

---

```
  ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗    ███╗   ███╗██╗███╗   ██╗██╗
 ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝    ████╗ ████║██║████╗  ██║██║
 ██║     ██║     ███████║██║   ██║██║  ██║█████╗      ██╔████╔██║██║██╔██╗ ██║██║
 ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝      ██║╚██╔╝██║██║██║╚██╗██║██║
 ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗    ██║ ╚═╝ ██║██║██║ ╚████║██║
  ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝    ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝
```

---

## 🧠 What Is This?

This is **Claude Mini** — a fully autonomous AI coding agent that:

1. Takes your instructions in plain English
2. Thinks about them (very hard, presumably)
3. Uses tools to read, write, and run code on your machine
4. Asks for your permission before doing anything dangerous (unlike some people)
5. **Completely built a Snake game from scratch, by itself, without being babysat**

It's powered by [OpenRouter](https://openrouter.ai), speaks the OpenAI API dialect, and connects to the world via **MCP (Model Context Protocol)** servers. Think of it as a very obedient intern who never sleeps, never asks for a raise, and occasionally writes surprisingly good Python.

---

## 🏗️ Architecture — The Boring (But Impressive) Stuff

```
claude-mini/
├── agent.py              ← The brain. The whole brain.
├── memory.md             ← The agent's diary (currently empty, it has no trauma yet)
├── workspace/
│   └── snake_game/
│       ├── snake.py      ← A fully playable Snake game. Written by an AI. Unassisted.
│       ├── test_snake.py ← 9 unit tests. Also written by the AI. They all pass.
│       └── README.md     ← The AI documented its own work. Overachiever.
├── .env                  ← Your secrets. Guard them with your life.
├── pyproject.toml        ← Python packaging, because we're professionals here
└── requirements.txt      ← The bare minimum to make this thing run
```

### Core Components

| Component | What It Does | Vibe |
|---|---|---|
| `AsyncOpenAI` client | Talks to the LLM via OpenRouter | The mouth |
| `TOOL_SCHEMAS` | Tells the LLM what tools exist | The hands |
| `run_agent()` | The agentic loop — keeps calling tools until done | The work ethic |
| `connect_mcp()` | Spins up MCP servers for time & web fetch | The internet connection |
| `load_memory()` / `save_memory()` | Persistent facts across sessions | The memory (better than mine) |
| `safe_path()` | Sandboxes all file ops to `/workspace` | The responsible adult |

---

## 🛠️ Tools the Agent Has Access To

The agent isn't just vibing — it has **real tools** it can call:

```
🗂️  list_files    → "What files do I have to work with?"
📖  read_file     → "Let me actually look before I touch anything"
✍️  write_file    → "I shall create. Or overwrite. Same thing."
💾  save_memory   → "I should remember this about the user"
💻  run_command   → "Run this shell command... if the human says yes"
🌐  fetch         → "Let me check the internet real quick"
🕐  time          → "What time is it? (Asking for a friend)"
```

> ⚠️ `run_command` requires **your explicit approval** before execution. The agent will literally ask `Run 'python snake.py'? [y/N]`. It respects consent. 10/10.

---

## 🐍 The Snake Game — A Love Story Between AI and Pygame (Except No Pygame)

Here's the wildest part: **the agent built a complete, working Snake game using only Python's standard library.**

No pip installs. No third-party dependencies. Just `tkinter` and pure, unadulterated algorithmic snake logic.

### What the AI Actually Built

**`Game` class** — Pure headless game logic, zero GUI dependencies:
- 20×20 grid, 120ms tick rate
- Collision detection (walls + self)
- Food spawning on random empty cells
- 180° turn prevention (no cheating)
- Pause, reset, and win condition (fill the entire board)
- Score tracking

**`SnakeApp` class** — The tkinter frontend:
- Dark theme (`#101418` background, because the AI has taste)
- Bright green snake (`#4ade80` head, `#22c55e` body)
- Red food (`#ef4444`)
- WASD + Arrow key support
- High score tracking across resets
- Game over overlay with stipple effect

**`test_snake.py`** — 9 headless unit tests covering:

```python
✅ test_step_moves_head
✅ test_eating_food_grows_and_scores
✅ test_wall_collision_ends_game
✅ test_self_collision_ends_game
✅ test_moving_into_tail_cell_is_allowed   ← the subtle one
✅ test_reverse_direction_is_ignored
✅ test_pause_blocks_stepping
✅ test_reset_clears_state
✅ test_full_board_is_a_win
```

The AI wrote the tests. The AI ran the tests. The AI fixed the bugs. The AI documented everything. You were probably asleep.

---

## 🚀 Getting Started

### Prerequisites

- Python ≥ 3.11
- `uv` (recommended) or `pip`
- An [OpenRouter](https://openrouter.ai) API key
- A `.env` file that looks like this:

```env
OPENROUTER_API_KEY=your_key_here
AI_MODEL=anthropic/claude-3-haiku   # or whatever model you're using
```

### Install & Run

```bash
# Clone or download this repo
cd claude-mini

# Install dependencies
uv sync
# or: pip install -r requirements.txt

# Launch the agent
python agent.py
```

You'll see:
```
 [mcp] connected: time: ['get_current_time']
 [mcp] connected: fetch: ['fetch']

Claude MINI

you: █
```

Now type anything. Ask it to build you a game. It will.

### Play the Snake Game

```bash
cd workspace/snake_game
python snake.py
```

| Key | Action |
|---|---|
| `↑ ↓ ← →` or `WASD` | Move |
| `P` | Pause / Resume |
| `R` | Restart |
| `Q` / `Esc` | Quit |

---

## 🧬 How the Agentic Loop Works

```
User types a message
        │
        ▼
  System prompt + memory injected
        │
        ▼
  LLM responds with tool_calls OR final text
        │
   ┌────┴────┐
   │         │
tool_calls  text → return to user ✅
   │
   ▼
Execute each tool (local or MCP)
   │
   ▼
Append tool results to messages
   │
   ▼
Loop back to LLM ↺
```

The agent keeps looping until the LLM stops calling tools and returns a plain text response. It's turtles all the way down, except the turtles are JSON tool calls.

---

## 🧠 Memory System

The agent has a `memory.md` file where it saves persistent facts about you:

```markdown
- User prefers Python over JavaScript.
- User is building a mini AI agent project.
- User asked the agent to build a Snake game and it delivered.
```

Every new session loads this memory into the system prompt. The agent remembers you. Whether that's comforting or unsettling is up to you.

---

## 📦 Dependencies

```toml
mcp >= 2.3.0          # Model Context Protocol — the agent's nervous system
openai >= 3.35.1      # OpenAI SDK (used with OpenRouter)
pydantic >= 2.14.1    # Data validation, because chaos is bad
python-dotenv >= 1.2.4 # .env file loading
asyncio >= 4.0.0      # Async everything, because we're not savages
```

The Snake game itself? **Zero extra dependencies.** Just Python. Just vibes.

---

## 🔒 Security Model

- All file operations are sandboxed to the `workspace/` directory via `safe_path()`
- Shell commands require **explicit user approval** (`[y/N]` prompt)
- No secrets are ever written to files or memory
- Path traversal attacks (`../../etc/passwd`) are blocked at the function level

The agent is powerful. The agent is also polite about it.

---

## 💡 The Philosophy

The system prompt says it best:

> *"Smallest change that solves the problem. Keep existing style and structure."*
> *"Never invent file contents, command output, or API behavior."*
> *"Direct. No filler, no flattery."*

This agent was built to be a **no-nonsense coding assistant** — not a yes-machine that hallucinates file contents and pretends everything worked. It reads before it writes. It runs before it claims success. It disagrees with you when you're wrong.

Basically, it's the senior engineer you always wanted but could never afford.

---

## 🎮 Proof It Works

The entire `workspace/snake_game/` directory was generated by the agent in a single session. The agent:

1. Listed the workspace (empty)
2. Planned the architecture (Game + SnakeApp separation)
3. Wrote `snake.py` with full game logic and tkinter UI
4. Wrote `test_snake.py` with 9 edge-case tests
5. Ran the tests via `run_command`
6. Fixed a subtle tail-collision bug it caught itself
7. Wrote the `README.md` for the game
8. Reported back with a clean summary

Zero human code was written. Zero. You just typed "build me a snake game" and went to get coffee.

---

## 🤝 Contributing

Found a bug? The agent probably already knows about it.

Want to add a feature? Ask the agent. It'll write the PR too, probably.

---

<div align="center">

**Built with 🐍 Python · Powered by 🤖 LLMs · Vibes by ☕ Coffee**

*"It's not about the destination. It's about the autonomous agent we made along the way."*

</div>
