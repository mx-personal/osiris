from osiris.model.agent import Agent
from osiris.model.context import Clock
import osiris.model.context as context
import datetime as dt
from dateutil import relativedelta

class Model():
    def __init__(self):
        pass

    def simulate(self, ts_start: dt.datetime, time_step: relativedelta):
        clock = Clock(ts_start=ts_start, time_step=time_step)
        historian = context.Historian()
        agent = Agent("agent", sim_step=clock.time_step)
        for i in range(24 * 10 * 3):
            agent.pick_action(clock.time)
            historian.update_log(id_agent=1, agent_state=agent.current_state, clock_state=clock.current_state)
            clock.tick()
        return historian.log

# ts_start=dt.datetime(2000, 1, 1, 0, 0, 0), time_step=relativedelta(minutes=10)
