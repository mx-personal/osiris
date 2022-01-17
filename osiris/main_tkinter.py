import osiris.view_tkinter as view
from osiris.model.model import Model
import tkinter as tk


class Controller():
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("500x500")
        self.model = Model()
        self.view = view.View(self.window)
        self.view.control_panel.frame.btn_simul.bind("<Button-1>", self.run_simulation)


    def run(self):
        self.window.mainloop()

    def run_simulation(self, event):
        results = self.model.simulate()
        x = results['clock']['ts']
        series_commod = []
        series_commod.append(("hunger", results['commod']['hunger']))
        series_commod.append(("energy", results['commod']['energy']))
        series_commod.append(("fun", results['commod']['fun']))

        # series_actions = []
        # series_actions.append(("sleep", results['actions']['sleep']))
        # series_actions.append(("eat", results['actions']['eat']))
        # series_actions.append(("work", results['actions']['work']))
        # series_actions.append(("watch tv", results['actions']['watch tv']))

        self.view.graph_panel.plot_series(x, series_commod)


def main():
    controller = Controller()
    controller.run()


if __name__ == "__main__":
    main()
