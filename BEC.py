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

if molasses_repump_int_start < molasses_repump_int_end:
    message = 'User Warning: Repump intensity ramps UP during molasses!'
    sys.stderr.write(message+'\n')

if molasses_duration*ms < max(B_bias_respond_time*ms,cooling_lock_time*ms):
    message = 'User Warning: Effectively no molasses because cooling light is turned off in advance in Optical pumping!'
    sys.stderr.write(message+'\n')
#)


'''

Sequence

'''

start()
t = 0
Initial_State(t)

t += 0.091

t = MOT_load(t)

if Do_MOT_quad_trap:
    t = CMOT(t)
    print('t='+str(t)+', CMOT done!')
    t = molasses(t)
    print('t='+str(t)+', Molasses done!')
    t = Opt_Pump(t)
    print('t='+str(t)+', Optical pumping done!')    
    t = MOT_cell_quad_trap(t)
    print('t='+str(t)+', MOT cell quad trap done!') 
    shutter_turn_on = True
else:
    shutter_turn_on = False

t = Imaging_prep(t)

t += TOF*ms
print('t='+str(t)+', TOF done!')

Fluo_image(t, 'fluo_img', shutter_turn_on=shutter_turn_on)

t += 0.5

Fluo_image(t, 'bg') # By default, shutters do not open in this function
print('t='+str(t)+', Experiment done!')

Initial_State(t)

t += 1
stop(t)
    