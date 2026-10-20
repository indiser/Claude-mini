# Pomodoro timer

A small desktop Pomodoro timer built with Python's standard library only
(`tkinter`, no pip installs needed).

## Run it

```
python pomodoro.py
```

## What it does

- Counts down a focus session, then a short break.
- After every 4 focus sessions you get a long break, and the set starts over.
- Progress bar, one dot per focus session in the current set, and a beep when
  a phase ends.
- **Settings** changes the focus / short break / long break lengths, how many
  sessions are in a set, and whether breaks and focus sessions start
  automatically. Settings are saved to `~/.pomodoro_settings.json`.

## Controls

| Button / key | Action |
| --- | --- |
| `Start` / `Pause`, `space` | start or pause the timer |
| `Reset`, `r` | back to a fresh focus session and clear the count |
| `Skip`, `s` | jump to the next phase (a skipped focus session is not counted) |
| `Settings` | edit durations and auto-start options |
| `q`, `Esc` | quit |

## Layout of the code

- `Pomodoro` — the timing rules (phases, countdowns, cycle). No GUI code, so
  it can be tested headlessly.
- `PomodoroApp` — the tkinter front end that renders a `Pomodoro`.
- `SettingsDialog` — the small window for editing the durations.

## Tests

```
python -m unittest test_pomodoro.py
```
