# # import pandas as pd
# # # mux = pd.MultiIndex.from_tuples(tuples=[(None,)*3],names=['one','two','three'])
# # mux = pd.MultiIndex.from_tuples(tuples=[('commo','hunger'),('commo','fun'),('sig','drowsy'),('sig','sunlight')])
# # data = [{('commo','hunger'):0,('commo','fun'):1,('sig','drowsy'):2,('sig','sunlight'):3},
# #         {('commo','hunger'):5,('commo','fun'):18,('sig','drowsy'):18,('sig','sunlight'):1}]
# #
# # foo = pd.DataFrame(columns=mux,data=data)
# # # foo = pd.DataFrame(data=data)
# # import pdb;pdb.set_trace()
#
# import datetime as dt
# from pprint import pprint
# # foo = dt.timedelta(minutes=10)
# # bar = [i*foo for i in range(int(24*60/10))]
# #
# # pprint(bar)
# # print(2*foo)
# hours_working = [(9, 13), (14, 18)]
# foo = dt.timedelta(minutes=10)
# ds = dt.datetime(2020, 1, 1, 0, 0, 0)
# bar = []
# for start, end in hours_working:
#         bar.extend([(ds + dt.timedelta(hours=start) + i * foo).time() for i in range(1, int((end - start)*60/10)+1)])
# bar2 = [dt.time(elt.hour,elt.minute) for elt in bar]
# # import pdb;pdb.set_trace()
# # ---------------------
#
# hours_working = {
#         0: [(9, 13), (14, 18)],
#         1: [(9, 13), (14, 18)],
#         2: [(9, 13)],
#         3: [(9, 13), (14, 18)],
#         4: [(9, 13), (14, 18)],
#         5: [],
#         6: [],
# }
#
# foo = dt.timedelta(minutes=10)
# ds = dt.datetime(2020, 1, 1, 0, 0, 0)
# bar = []
# for k in hours_working:
#         for start, end in hours_working[k]:
#                 bar.extend([(k,(ds + dt.timedelta(hours=start) + i * foo).time()) for i in range(1, int((end - start)*60/10)+1)])
# bar2 = set(bar)
# pprint(bar)

import calendar
foo = calendar.Calendar()
import pdb;pdb.set_trace()