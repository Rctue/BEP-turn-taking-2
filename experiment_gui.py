# experiment_gui.py 
"""A lightweight GUI wrapper around the console based Misty state machine.

Why this file?
──────────────
* Replace raw terminal I/O by a nice dark themed window so you can show the
  experiment to participants.
* Everything that normally goes to *stdout* appears in the log pane.
* Everything that normally comes from `input()` is typed in the entry field.
* All `msvcrt.getch()` operator keys are mapped to buttons on the right.
* The GUI itself does **not** run in a separate thread; the *launcher* keeps the
  Tk main loop in the main thread.

How to integrate?
─────────────────
1. Keep your original `Hardcoded_experiment_code_new.py` unchanged.
2. Create a tiny `run_experiment_gui.py` (see docs / earlier messages) that:
     * calls `gui = setup_gui()`
     * starts your `main()` in a background thread
     * calls `gui.root.mainloop()`
3. Run that launcher. Thats it.

Design choices
──────────────
* Dark VS Code style colours.
* Left side is the scrollable log; right side operator buttons.
* Prompts (questions) in blue **bold**, answers in yellow *italic*.
* `[DEBUG]` lines can be shown/hidden with the **DBG** toggle.
"""

import tkinter as tk, sys, types
from queue import Queue

# ---------------------------------------------------------------------------
#                        Colour & style constants
# ---------------------------------------------------------------------------
BG      = "#1e1e1e"          # window background
CARD_BG = "#252526"          # grey card background
FG_TXT  = "#e0e0e0"          # regular foreground text
FONT    = ("Consolas", 10)   # monospaced font for log & entry
ACCENT  = "#0e639c"          # bright blue accent (buttons)

# ---------------------------------------------------------------------------
class ExperimentGUI:
    """Build the Tk window *and* patch stdin/stdout/msvcrt.*"""

    def __init__(self):
        # Queue used as a virtual stdin                 ↓----
        self.input_queue: "Queue[str]" = Queue()

        # ------------------ root window ----------------------------------
        self.root = tk.Tk()
        self.root.title("Misty Turn‑Taking Experiment")
        self.root.configure(bg=BG)

        # ------------------ title header ---------------------------------
        tk.Label(self.root,
                 text="Misty Turn‑Taking Experiment",
                 bg=BG, fg="#ffffff", font=("Segoe UI", 16, "bold")
                 ).pack(pady=(12, 6))

        # ------------------ card container -------------------------------
        card = tk.Frame(self.root, bg=CARD_BG)
        card.pack(padx=16, pady=(0, 12), fill="both", expand=True)

        # card has 2 columns: log (left) and operator buttons (right)
        log_frame  = tk.Frame(card, bg=CARD_BG)
        ctrl_frame = tk.Frame(card, bg=CARD_BG)
        log_frame.pack(side="left", fill="both", expand=True)
        ctrl_frame.pack(side="right", fill="y")

        # ------------------ log widget -----------------------------------
        # A simple Text + vertical Scrollbar
        scrollbar = tk.Scrollbar(log_frame)
        self.text = tk.Text(
            log_frame, wrap="word", yscrollcommand=scrollbar.set,
            bg="#0d0d0d", fg=FG_TXT, insertbackground="#ffffff",
            font=FONT, relief="flat", padx=6, pady=4, height=28
        )
        scrollbar.config(command=self.text.yview)
        scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        # colour tags for different kinds of lines
        self.text.tag_config("misty",  foreground="#4ec9b0")
        self.text.tag_config("prompt", foreground="#569cd6",
                              font=("Consolas", 10, "bold"))
        self.text.tag_config("user",   foreground="#dcdcaa",
                              font=("Consolas", 10, "italic"))
        self.text.tag_config("debug",  foreground="#6a9955")

        # ------------------ operator buttons -----------------------------
        # 8 experiment control keys + one DBG toggle
        btn_style = dict(bg="#3a3d41", fg="#d4d4d4",
                          activebackground="#4b4f55", relief="flat", width=9)
        for key, lbl in [
            ("c", "Long"), ("d", "Swch"), ("t", "Turn"), ("i", "Info"),
            ("v", "Vrct"), ("q", "Next"), ("r", "Rpt"),  ("a", "Auto")]:
            tk.Button(ctrl_frame, text=f"{lbl}\n({key})",
                      command=lambda k=key: self._enqueue(k), **btn_style
                      ).pack(pady=2)

        # DEBUG toggle hides/shows the [DEBUG] lines without deleting them
        self.debug_visible = True
        def _toggle_debug():
            self.debug_visible = not self.debug_visible
            self.text.tag_config("debug", elide=not self.debug_visible)
        tk.Button(ctrl_frame, text="DBG", width=9, command=_toggle_debug,
                  bg=ACCENT, fg="#fff", relief="flat").pack(pady=6)

        # ------------------ input field + Submit button ------------------
        input_frame = tk.Frame(self.root, bg=BG)
        self.entry = tk.Entry(input_frame, font=FONT, bg="#1b1b1b", fg=FG_TXT,
                              insertbackground="#ffffff", relief="flat")
        self.entry.pack(side="left", padx=(0, 8), ipady=4, fill="x", expand=True)
        tk.Button(input_frame, text="Submit", width=12, command=self._on_enter,
                  bg=ACCENT, fg="#ffffff", relief="flat",
                  activebackground="#1177bb").pack(side="left")
        input_frame.pack(padx=16, pady=(0, 14), fill="x")

        # focus on entry & <Return> anywhere submits
        self.entry.focus_set()
        self.root.bind("<Return>", self._on_enter)

        # ------------------ std‑in/out monkey patches --------------------
        sys.stdout = sys.stderr = self                  # redirect prints
        import builtins; builtins.input = self._readline  # replace input()

        # replace msvcrt.kbhit/getch so operator keys still work
        try:
            import msvcrt                              # Windows
        except ImportError:                            # mac/Linux
            msvcrt = types.ModuleType("msvcrt")
            sys.modules["msvcrt"] = msvcrt
        msvcrt.kbhit = lambda: not self.input_queue.empty()
        msvcrt.getch  = lambda: self.input_queue.get().encode("ascii")

    # -------------------------------------------------------------------
    #              stdout‑like object so `print()` writes to GUI
    # -------------------------------------------------------------------
    def write(self, msg:str, tag:str|None = None):
        """Append *msg* to the Text widget – thread‑safe via .after()."""
        if not msg:
            return
        # ensure every message ends with newline so each appears on a new line
        if not msg.endswith("\n"):
            msg += "\n"
        # auto‑tag if not provided
        if tag is None:
            tag = ("misty"  if msg.lstrip().startswith("[MISTY]") else
                   "debug" if msg.lstrip().startswith("[DEBUG]") else None)
        # schedule GUI update in the Tk thread
        self.text.after(0, self._append, msg, tag)

    def flush(self):  # needed because `print()` may call flush()
        pass

    def _append(self, msg:str, tag:str|None):
        """Actually insert text – runs inside the Tk thread."""
        self.text.insert(tk.END, msg, (tag,) if tag else ())
        self.text.see(tk.END)

    # -------------------------------------------------------------------
    #                       Reading from the GUI
    # -------------------------------------------------------------------
    def _on_enter(self, _=None):
        """User pressed <Return> or clicked *Submit*."""
        txt = self.entry.get().strip()
        if not txt:
            return  # ignore empty lines
        self.entry.delete(0, tk.END)
        self._enqueue(txt)           # make it available to `input()`
        self.write(txt, "user")      # echo back in yellow italic

    def _enqueue(self, txt:str):
        self.input_queue.put(txt)

    def _readline(self, prompt:str="") -> str:
        """Replacement for builtins.input()"""
        if prompt:
            self.write(prompt.rstrip(), "prompt")
        return self.input_queue.get().rstrip("\r\n")

# ---------------------------------------------------------------------------
# Helper for external modules – simply call gui = setup_gui()
# ---------------------------------------------------------------------------

def setup_gui() -> ExperimentGUI:
    """Create the GUI and return the instance."""
    return ExperimentGUI()
