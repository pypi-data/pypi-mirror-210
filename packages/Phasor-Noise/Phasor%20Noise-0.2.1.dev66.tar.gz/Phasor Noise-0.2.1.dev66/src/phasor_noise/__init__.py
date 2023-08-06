import tkinter as tk
from phasor_noise.GUI import Window


def default_window():
    """
    Easy first window to manipulate the phasor noise and observe it
    """

    root = tk.Tk()
    Window(root)
    root.mainloop()
