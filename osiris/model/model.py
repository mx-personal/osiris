from osiris.model.agent import Agent
from osiris.model.context import Clock
import osiris.model.context as context
import datetime as dt
from dateutil import relativedelta
import os

class Model():
    def __init__(self):
        pass

    def simulate(self, ts_start: dt.datetime, time_step: relativedelta):
        clock = Clock(ts_start=ts_start, time_step=time_step)
        historian = context.Historian()
        # agent = Agent("agent", sim_step=clock.time_step)
        path_internal = os.path.join(os.path.dirname(__file__))
        agent = Agent.from_config_file(
            name="agent",
            sim_step=clock.time_step,
            path=r"{0}\parameters\config_agent_actions.yaml".format(path_internal)
        )
        for i in range(24 * 10 * 3):
            agent.pick_action(clock.time)
            historian.update_log(id_agent=1, agent_state=agent.current_state, clock_state=clock.current_state)
            clock.tick()
        return historian.log


if __name__ == "__main__":
    model = Model()
    model.simulate(ts_start=dt.datetime(year=2000,month=1,day=1), time_step=relativedelta.relativedelta(minutes=10))
