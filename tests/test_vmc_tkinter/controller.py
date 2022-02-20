import tkinter as Tk
from tests.test_vmc_tkinter.model import Model
from tests.test_vmc_tkinter.view import View


class Controller():
    def __init__(self):
        self.root = Tk.Tk()
        self.model = Model()
        self.view = View(self.root)
        self.view.sidepanel.plotBut.bind("&lt;Button&gt;", self.my_plot)
        self.view.sidepanel.clearButton.bind("&lt;Button&gt;", self.clear)

    def run(self):
        self.root.title("Tkinter MVC example")
        self.root.deiconify()
        self.root.mainloop()

    def clear(self, event):
        self.view.ax0.clear()
        self.view.fig.canvas.draw()

    def my_plot(self, event):
        self.model.calculate()
        self.view.ax0.clear()
        self.view.ax0.contourf(self.model.res["x"], self.model.res["y"], self.model.res["z"])
        self.view.fig.canvas.draw()

