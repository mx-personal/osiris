from osiris.model.agent import Agent
from osiris.model.context import Clock
import osiris.model.context as context

class Model():
    def __init__(self):
        pass

    def simulate(self):
        clock = Clock()
        historian = context.Historian()
        agent = Agent("agent", sim_step=clock.time_step)
        for i in range(24 * 10 * 3):
            agent.pick_action(clock.time)
            historian.update_log(id_agent=1, agent_state=agent.current_state, clock_state=clock.current_state)
            clock.tick()
        return historian.log