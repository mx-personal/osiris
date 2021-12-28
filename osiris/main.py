from osiris.agent import Agent
from osiris.context import Clock
import pdb

def main():
    clock = Clock()
    koro = Agent("koro", sim_step=clock.time_step)
    for i in range(24*10*10):
        koro.pick_action(clock.time)
        clock.tick()
    pdb.set_trace()
    # koro.display_results()


if __name__ == "__main__":
    main()
