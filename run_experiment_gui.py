# run_experiment_gui.py
"""
Launch the Misty state-machine with the custom GUI.

• Always start THIS file instead of Hardcoded_experiment_code_new.py.
• The GUI (Tk main-loop) stays in the main thread.
• The state-machine runs in a background thread so the window stays responsive.
"""

#DON'T FORGET: 
# !!!!Always choose open_70.jpg from the web interface of Misty BEFORE starting the experiment!!!
# Otherwise you can see for a brief moment the default eye image. 

from experiment_gui import setup_gui
import threading

# Import your state-machine module.
import Hardcoded_experiment_code_new as sm

# 1) Create and show the GUI window
gui = setup_gui()

# 2) Run the state-machine in a separate daemon thread
threading.Thread(target=sm.main, daemon=True).start()

# 3) Start the Tk event-loop in the main thread (required on Windows)
gui.root.mainloop()

