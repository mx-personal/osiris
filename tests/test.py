from osiris.model.model import Model
from dateutil.relativedelta import relativedelta
import datetime as dt

model = Model()
results = model.simulate(ts_start=dt.datetime(year=2000,month=1,day=1), time_step=relativedelta(minutes=10))

import pdb;pdb.set_trace()