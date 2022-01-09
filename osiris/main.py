from osiris.model.agent import Agent
from osiris.model.context import Clock
import osiris.model.context as context
import osiris.view as view
import tkinter as tk

class Model():
    def __init__(self):
        pass

    def simulate(self):
        clock = Clock()
        historian = context.Historian()
        agent = Agent("agent", sim_step=clock.time_step)
        for i in range(24*10*10):
            agent.pick_action(clock.time)
            historian.update_log(id_agent=1, agent_state=agent.current_state, clock_state=clock.current_state)
            clock.tick()
        return historian.log


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
        print(results)
        x = results['clock']['ts']
        series_commod = []
        series_commod.append(("hunger", results['commod']['hunger']))
        series_commod.append(("energy", results['commod']['energy']))
        series_commod.append(("fun", results['commod']['fun']))

        series_actions = []
        series_actions.append(("sleep", results['actions']['sleep']))
        series_actions.append(("eat", results['actions']['eat']))
        series_actions.append(("work", results['actions']['work']))
        series_actions.append(("watch tv", results['actions']['watch tv']))

        self.view.graph_panel.plot_series_2(x, series_commod, series_actions)


def main():
    controller = Controller()
    controller.run()


if __name__ == "__main__":
    main()
