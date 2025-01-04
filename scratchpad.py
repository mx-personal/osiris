import yaml
import os

root = os.path.dirname(os.path.abspath(__file__))
path_configs = os.path.join(root, 'sim_config.yaml')

with open(path_configs) as f:
    configs = yaml.safe_load(f)

import pdb;pdb.set_trace()
