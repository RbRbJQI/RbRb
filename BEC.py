from labscript import *
from labscriptlib.common.utils import Limits
from labscriptlib.common.functions import *
from labscript_utils import import_or_reload
from labscriptlib.RbRb.BEC_functions import *

import_or_reload('labscriptlib.RbRb.connection_table')

MHz = 1e6
us = 1e-6
ms = 1e-3

'''

Warnings: Don't do stupid things!

'''
#(
if not all(v == 0 for v in [B_zero_x,B_zero_y,B_zero_z]):
    raise Warning("B_zero" r"$\neq$" "0!")
#)

'''

Sequence

'''

start()
t = 0
Initial_State(t)

t += 0.1

t = MOT_load(t, np.array([MOT_B_bias_x,MOT_B_bias_y, MOT_B_bias_z]))

t = Imaging_prep(t)

t += TOF

t = Fluo_image(t, Fluo_image_duration, 'fluo_img')

t += 0.5

t = Fluo_image(t, Fluo_image_duration, 'bg')


Initial_State(t)

t += 1
stop(t)
    