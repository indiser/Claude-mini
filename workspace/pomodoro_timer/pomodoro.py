"""Pomodoro timer — standard library only (tkinter).

The timing rules live in `Pomodoro`, which has no GUI dependencies and can be
tested headlessly. `PomodoroApp` renders a `Pomodoro` with tkinter.

Run:  python pomodoro.py
"""

import json
import os
import sys

# --- Configuration -----------------------------------------------------------

WORK = "work"
SHORT_BREAK = "short_break"
LONG_BREAK = "long_break"

PHASE_LABELS = {
    WORK: "Focus",
    SHORT_BREAK: "Short break",
    LONG_BREAK: "Long break",
}

DEFAULT_WORK_MINUTES = 25
DEFAULT_SHORT_BREAK_MINUTES = 5
DEFAULT_LONG_BREAK_MINUTES = 15
DEFAULT_LONG_BREAK_EVERY = 4

SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".pomodoro_settings.json")

# --- Colours -----------------------------------------------------------------

BG = "#101418"
PANEL = "#1b2027"
TEXT = "#e5e7eb"
MUTED = "#9aa4b2"
ACCENT = "#4ade80"
WORK_COLOR = "#ef4444"
BREAK_COLOR = "#38bdf8"


# --- Helpers -----------------------------------------------------------------


def format_time(seconds):
    """Format a number of seconds as MM:SS."""
    minutes, seconds = divmod(max(0, int(seconds)), 60)
    return f"{minutes:02d}:{seconds:02d}"


def load_settings(path=SETTINGS_FILE):
    """Read saved settings, falling back to the defaults on any problem."""
    settings = {
        "work_minutes": DEFAULT_WORK_MINUTES,
        "short_break_minutes": DEFAULT_SHORT_BREAK_MINUTES,
        "long_break_minutes": DEFAULT_LONG_BREAK_MINUTES,
        "long_break_every": DEFAULT_LONG_BREAK_EVERY,
        "auto_start_break": True,
        "auto_start_work": False,
    }
    try:
        with open(path, "r", encoding="utf-8") as handle:
            saved = json.load(handle)
    except (OSError, ValueError):
        return settings

    for key in settings:
        if key in saved:
            settings[key] = saved[key]
    return settings


def save_settings(settings, path=SETTINGS_FILE):
    """Write settings to disk; failures are ignored (the app still works)."""
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, indent=2)
    except OSError:
        pass


# --- Game logic --------------------------------------------------------------


class Pomodoro:
    """Counts down work and break phases, cycling between them."""

    def __init__(
        self,
        work_minutes=DEFAULT_WORK_MINUTES,
        short_break_minutes=DEFAULT_SHORT_BREAK_MINUTES,
        long_break_minutes=DEFAULT_LONG_BREAK_MINUTES,
        long_break_every=DEFAULT_LONG_BREAK_EVERY,
        auto_start_break=True,
        auto_start_work=False,
    ):
        self.work_minutes = int(work_minutes)
        self.short_break_minutes = int(short_break_minutes)
        self.long_break_minutes = int(long_break_minutes)
        self.long_break_every = max(1, int(long_break_every))
        self.auto_start_break = bool(auto_start_break)
        self.auto_start_work = bool(auto_start_work)
        self.reset()

    # -- state ---------------------------------------------------------------

    @property
    def phase(self):
        """The phase that is currently counting down."""
        return self._phase

    @property
    def running(self):
        return self._running

    @property
    def remaining(self):
        """Seconds left in the current phase."""
        return self._remaining

    @property
    def completed(self):
        """Total number of finished focus sessions."""
        return self._completed

    @property
    def sessions_in_set(self):
        """Focus sessions finished in the current set of `long_break_every`."""
        return self._sessions_in_set

    @property
    def is_break(self):
        return self._phase in (SHORT_BREAK, LONG_BREAK)

    # -- durations -----------------------------------------------------------

    def phase_length(self, phase=None):
        """Length of a phase in seconds."""
        phase = phase or self._phase
        minutes = {
            WORK: self.work_minutes,
            SHORT_BREAK: self.short_break_minutes,
            LONG_BREAK: self.long_break_minutes,
        }[phase]
        return max(0, minutes) * 60

    def progress(self):
        """How much of the current phase is done, from 0.0 to 1.0."""
        total = self.phase_length()
        if total <= 0:
            return 0.0
        done = total - self._remaining
        return min(1.0, max(0.0, done / total))

    # -- controls ------------------------------------------------------------

    def reset(self):
        """Start over: a fresh focus session, paused, with the count cleared."""
        self._phase = WORK
        self._remaining = self.phase_length(WORK)
        self._running = False
        self._completed = 0
        self._sessions_in_set = 0

    def start(self):
        self._running = True

    def pause(self):
        self._running = False

    def toggle(self):
        """Start when paused, pause when running."""
        self._running = not self._running
        return self._running

    def apply_settings(
        self,
        work_minutes=None,
        short_break_minutes=None,
        long_break_minutes=None,
        long_break_every=None,
        auto_start_break=None,
        auto_start_work=None,
    ):
        """Apply new durations, keeping the current phase and run state."""
        if work_minutes is not None:
            self.work_minutes = int(work_minutes)
        if short_break_minutes is not None:
            self.short_break_minutes = int(short_break_minutes)
        if long_break_minutes is not None:
            self.long_break_minutes = int(long_break_minutes)
        if long_break_every is not None:
            self.long_break_every = max(1, int(long_break_every))
        if auto_start_break is not None:
            self.auto_start_break = bool(auto_start_break)
        if auto_start_work is not None:
            self.auto_start_work = bool(auto_start_work)

        self._remaining = min(self._remaining, self.phase_length())
        if self._remaining <= 0:
            self._remaining = self.phase_length()

    # -- running -------------------------------------------------------------

    def tick(self):
        """Advance one second. Returns the finished phase, or None."""
        if not self._running:
            return None

        self._remaining -= 1
        if self._remaining > 0:
            return None

        finished = self._phase
        if finished == WORK:
            self._completed += 1
            self._sessions_in_set += 1
            if self._sessions_in_set >= self.long_break_every:
                self._enter(LONG_BREAK)
            else:
                self._enter(SHORT_BREAK)
        else:
            self._enter(WORK)
        return finished

    def skip(self):
        """Jump straight to the next phase. Returns the phase that was left.

        A skipped focus session is not counted, so it never counts towards the
        long break either.
        """
        left = self._phase
        if left == WORK:
            self._enter(SHORT_BREAK, auto_start=self._running)
        else:
            self._enter(WORK, auto_start=self._running)
        return left

    def _auto_start_for(self, phase):
        if phase == WORK:
            return self.auto_start_work
        return self.auto_start_break

    def _enter(self, phase, auto_start=None):
        """Switch to a new phase and reload its countdown."""
        if phase == WORK and self._phase == LONG_BREAK:
            # the set is over, the next focus session starts a fresh one
            self._sessions_in_set = 0

        self._phase = phase
        self._remaining = self.phase_length()
        if auto_start is None:
            auto_start = self._auto_start_for(phase)
        self._running = auto_start


# --- User interface ----------------------------------------------------------


class PomodoroApp:
    """Tkinter front end for `Pomodoro`."""

    BAR_WIDTH = 320
    BAR_HEIGHT = 14
    DOT_SIZE = 10
    DOT_GAP = 8

    def __init__(self, root, timer=None):
        import tkinter as tk

        self.tk = tk
        self.root = root
        self.timer = timer or Pomodoro()

        root.title("Pomodoro")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.phase_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.count_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready when you are.")
        self.button_var = tk.StringVar()

        self._build()
        self._refresh()
        root.bind("<KeyPress>", self.on_key)
        self.root.after(1000, self.on_tick)

    # -- layout --------------------------------------------------------------

    def _build(self):
        tk = self.tk

        tk.Label(
            self.root,
            textvariable=self.phase_var,
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(24, 4))

        tk.Label(
            self.root,
            textvariable=self.time_var,
            bg=BG,
            fg=TEXT,
            font=("Consolas", 64, "bold"),
        ).pack()

        self.bar = tk.Canvas(
            self.root,
            width=self.BAR_WIDTH,
            height=self.BAR_HEIGHT,
            bg=BG,
            highlightthickness=0,
        )
        self.bar.pack(pady=(0, 6))

        self.dots = tk.Canvas(
            self.root,
            width=self.BAR_WIDTH,
            height=self.DOT_SIZE + 4,
            bg=BG,
            highlightthickness=0,
        )
        self.dots.pack(pady=(0, 10))

        buttons = tk.Frame(self.root, bg=BG)
        buttons.pack()

        tk.Button(
            buttons,
            textvariable=self.button_var,
            width=10,
            command=self.on_start,
            font=("Segoe UI", 11),
        ).grid(row=0, column=0, padx=4)

        tk.Button(
            buttons,
            text="Reset",
            width=10,
            command=self.on_reset,
            font=("Segoe UI", 11),
        ).grid(row=0, column=1, padx=4)

        tk.Button(
            buttons,
            text="Skip",
            width=10,
            command=self.on_skip,
            font=("Segoe UI", 11),
        ).grid(row=0, column=2, padx=4)

        tk.Button(
            buttons,
            text="Settings",
            width=10,
            command=self.on_settings,
            font=("Segoe UI", 11),
        ).grid(row=0, column=3, padx=4)

        tk.Label(
            self.root,
            textvariable=self.count_var,
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(pady=(14, 2))

        tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 10),
        ).pack(pady=(2, 18))

        tk.Label(
            self.root,
            text="space: start/pause    r: reset    s: skip    q: quit",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(pady=(0, 14))

    # -- input ---------------------------------------------------------------

    def on_key(self, event):
        key = event.keysym.lower()

        if key == "space":
            self.on_start()
        elif key == "r":
            self.on_reset()
        elif key == "s":
            self.on_skip()
        elif key in ("escape", "q"):
            self.root.destroy()

    def on_start(self):
        self.timer.toggle()
        self.status_var.set("Running." if self.timer.running else "Paused.")
        self._refresh()

    def on_reset(self):
        self.timer.reset()
        self.status_var.set("Timer reset. Ready for a new focus session.")
        self._refresh()

    def on_skip(self):
        left = self.timer.skip()
        self.status_var.set(f"Skipped the {PHASE_LABELS[left].lower()}.")
        self._refresh()

    def on_settings(self):
        SettingsDialog(self.root, self.timer, self._apply_settings)

    def _apply_settings(self, values):
        """Called by the settings dialog with the edited values."""
        self.timer.apply_settings(**values)
        save_settings(
            {
                "work_minutes": self.timer.work_minutes,
                "short_break_minutes": self.timer.short_break_minutes,
                "long_break_minutes": self.timer.long_break_minutes,
                "long_break_every": self.timer.long_break_every,
                "auto_start_break": self.timer.auto_start_break,
                "auto_start_work": self.timer.auto_start_work,
            }
        )
        self.status_var.set("Settings saved.")
        self._refresh()

    # -- loop ----------------------------------------------------------------

    def on_tick(self):
        finished = self.timer.tick()
        if finished is not None:
            self._announce(finished)
        self._refresh()
        self.root.after(1000, self.on_tick)

    def _announce(self, finished):
        self._play_sound()
        if finished == WORK:
            self.status_var.set("Focus session done — time for a break.")
        else:
            self.status_var.set("Break over — back to work.")

    def _play_sound(self):
        try:
            import winsound

            winsound.MessageBeep()
        except Exception:
            try:
                self.root.bell()
            except Exception:
                pass

    # -- drawing -------------------------------------------------------------

    def _refresh(self):
        timer = self.timer
        color = BREAK_COLOR if timer.is_break else WORK_COLOR

        self.time_var.set(format_time(timer.remaining))
        self.phase_var.set(PHASE_LABELS[timer.phase])
        self.button_var.set("Pause" if timer.running else "Start")
        self.count_var.set(
            f"{timer.completed} focus session(s) done   "
            f"({timer.sessions_in_set} of {timer.long_break_every} in this set)"
        )
        self._draw_bar(color)
        self._draw_dots(color)

    def _draw_bar(self, color):
        canvas = self.bar
        canvas.delete("all")

        width, height = self.BAR_WIDTH, self.BAR_HEIGHT
        canvas.create_rectangle(0, 0, width, height, fill=PANEL, outline="")

        filled = width * self.timer.progress()
        if filled > 0:
            canvas.create_rectangle(0, 0, filled, height, fill=color, outline="")

    def _draw_dots(self, color):
        """One dot per focus session in the current set."""
        canvas = self.dots
        canvas.delete("all")

        count = self.timer.long_break_every
        done = self.timer.sessions_in_set
        size = self.DOT_SIZE
        gap = self.DOT_GAP
        total = count * size + (count - 1) * gap
        x = (self.BAR_WIDTH - total) / 2
        y = 2

        for index in range(count):
            filled = index < done
            canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill=color if filled else PANEL,
                outline=MUTED,
            )
            x += size + gap


class SettingsDialog:
    """Small window for editing the timer durations."""

    def __init__(self, parent, timer, on_apply):
        import tkinter as tk

        self.tk = tk
        self.timer = timer
        self.on_apply = on_apply

        self.top = tk.Toplevel(parent)
        self.top.title("Pomodoro settings")
        self.top.configure(bg=BG)
        self.top.transient(parent)
        self.top.resizable(False, False)

        self.fields = {}
        rows = [
            ("Focus (minutes)", "work_minutes", 1, 180),
            ("Short break (minutes)", "short_break_minutes", 1, 90),
            ("Long break (minutes)", "long_break_minutes", 1, 180),
            ("Long break every (sessions)", "long_break_every", 1, 12),
        ]

        frame = tk.Frame(self.top, bg=BG)
        frame.pack(padx=18, pady=14)

        for row, (label, key, low, high) in enumerate(rows):
            tk.Label(
                frame, text=label, bg=BG, fg=TEXT, font=("Segoe UI", 10)
            ).grid(row=row, column=0, sticky="w", pady=4)
            var = tk.IntVar(value=getattr(timer, key))
            tk.Spinbox(
                frame,
                from_=low,
                to=high,
                textvariable=var,
                width=6,
                font=("Segoe UI", 10),
            ).grid(row=row, column=1, padx=(12, 0), pady=4)
            self.fields[key] = var

        self.auto_break = tk.BooleanVar(value=timer.auto_start_break)
        self.auto_work = tk.BooleanVar(value=timer.auto_start_work)

        tk.Checkbutton(
            frame,
            text="Start breaks automatically",
            variable=self.auto_break,
            bg=BG,
            fg=TEXT,
            activebackground=BG,
            activeforeground=TEXT,
            selectcolor=PANEL,
            font=("Segoe UI", 10),
        ).grid(row=len(rows), column=0, columnspan=2, sticky="w", pady=(10, 0))

        tk.Checkbutton(
            frame,
            text="Start focus sessions automatically",
            variable=self.auto_work,
            bg=BG,
            fg=TEXT,
            activebackground=BG,
            activeforeground=TEXT,
            selectcolor=PANEL,
            font=("Segoe UI", 10),
        ).grid(row=len(rows) + 1, column=0, columnspan=2, sticky="w", pady=(2, 0))

        buttons = tk.Frame(self.top, bg=BG)
        buttons.pack(pady=(0, 14))

        tk.Button(
            buttons,
            text="Cancel",
            width=10,
            command=self.top.destroy,
            font=("Segoe UI", 10),
        ).grid(row=0, column=0, padx=4)

        tk.Button(
            buttons, text="Save", width=10, command=self.save, font=("Segoe UI", 10)
        ).grid(row=0, column=1, padx=4)

        self.top.grab_set()

    def save(self):
        values = {key: int(var.get()) for key, var in self.fields.items()}
        values["auto_start_break"] = self.auto_break.get()
        values["auto_start_work"] = self.auto_work.get()
        self.on_apply(values)
        self.top.destroy()


def main():
    import tkinter as tk

    settings = load_settings()
    timer = Pomodoro(
        work_minutes=settings["work_minutes"],
        short_break_minutes=settings["short_break_minutes"],
        long_break_minutes=settings["long_break_minutes"],
        long_break_every=settings["long_break_every"],
        auto_start_break=settings["auto_start_break"],
        auto_start_work=settings["auto_start_work"],
    )

    root = tk.Tk()
    PomodoroApp(root, timer)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
