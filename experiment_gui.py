# experiment_gui.py
import tkinter as tk
import sys
import threading
from queue import Queue

class ExperimentGUI:
    def __init__(self):
        self.input_queue = Queue()
        self.root = tk.Tk()
        self.root.title("Misty Experiment")

        self.text = tk.Text(self.root, height=30, width=100, bg="black", fg="white", font=("Courier", 10))
        self.text.pack(padx=10, pady=(10,0))

        self.entry = tk.Entry(self.root, font=("Courier", 10), width=100)
        self.entry.pack(padx=10, pady=(5,10))
        self.entry.bind("<Return>", self.on_enter)

        self._orig_stdout = sys.stdout
        self._orig_stdin = sys.stdin

        sys.stdout = self
        sys.stdin = self

        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def write(self, message):
        self.text.insert(tk.END, str(message))
        self.text.see(tk.END)

    def flush(self):
        pass

    def on_enter(self, event=None):
        text = self.entry.get()
        self.entry.delete(0, tk.END)
        self.input_queue.put(text + '\n')

    def readline(self):
        return self.input_queue.get()

    def restore(self):
        sys.stdout = self._orig_stdout
        sys.stdin = self._orig_stdin
        
        
def setup_gui():
    gui = ExperimentGUI()
    threading.Thread(target=gui.root.mainloop, daemon=True).start()
    sys.stdin = gui
    sys.stdout = gui
    return gui 


#THIS NEEDS TO BE IN THE HARDCODED FILE
#import GUI
#from experiment_gui import setup_gui
#gui = setup_gui()
