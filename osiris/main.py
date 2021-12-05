from osiris.agent import Agent
from context import Clock

if __name__ == "__main__":
    clock = Clock()
    koro = Agent("koro",sim_step=clock.time_step)
    for i in range(24*10*10):
        koro.pick_action(clock.time)
        clock.tick()
    koro.display_results()
    import pdb;pdb.set_trace()
