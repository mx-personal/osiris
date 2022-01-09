import tkinter as tk
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use("TkAgg")


class View(object):
    def __init__(self, master):
        # self.frame = tk.Frame(master)
        self.control_panel = ControlPanel(master)
        self.graph_panel = GraphPanel(master)


class ControlPanel(object):
    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.frame.btn_simul = tk.Button(master, text="go", fg='blue')
        # self.frame.btn_simul.place(side=tk.LEFT, padx=15, pady=20)
        self.frame.btn_simul.pack(side=tk.TOP, padx=0, pady=0)


class GraphPanel(object):
    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.frame.pack(side=tk.BOTTOM, fill=tk.BOTH)

    def plot_series(self, x, series: []):
        fig = Figure(figsize=(20, 20), dpi=100)
        a = fig.add_subplot(1, 1, 1)
        for name_series, values_series in series:
            a.plot(x, values_series, label=name_series)
        a.legend()
        a.grid()
        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        get_widz = canvas.get_tk_widget()
        get_widz.pack()
