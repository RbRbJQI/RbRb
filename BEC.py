from labscript import *
from labscriptlib.common.utils import Limits
from labscriptlib.common.functions import *
from labscript_utils import import_or_reload
from labscriptlib.RbRb.BEC_functions import *
import sys

import_or_reload('labscriptlib.RbRb.connection_table')

MHz = 1e6
us = 1e-6
ms = 1e-3

'''

Warnings: Don't do stupid things!

'''
#(
if not [B_zero_x,B_zero_y,B_zero_z]==[0,0,0]:
    message = 'User Warning: B_zero !=0. These values should be coded in unitconversions!'
    sys.stderr.write(message+'\n')
#)

'''

Sequence

'''

start()
t = 0
Initial_State(t)

t += 0.1

t = MOT_load(t)

if Do_MOT_quad_trap:
    t = CMOT(t)
    t = molasses(t)
    t = Opt_Pump(t)
    t = MOT_cell_quad_trap(t)
    shutter_turn_on = True
else:
    shutter_turn_on = False

t = Imaging_prep(t)

t += TOF*ms

t = Fluo_image(t, Fluo_image_duration, 'fluo_img', shutter_turn_on=shutter_turn_on)

t += 0.5
print(t)
t = Fluo_image(t, Fluo_image_duration, 'bg', shutter_turn_on=shutter_turn_on)


Initial_State(t)

t += 1
stop(t)
    