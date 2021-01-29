from labscript import *
from labscriptlib.common.utils import Limits
from labscriptlib.common.functions import *
from labscript_utils import import_or_reload

import_or_reload('labscriptlib.RbRb.BEC_functions') # to make sure the globals in runmanager are reloaded
from labscriptlib.RbRb.BEC_functions import *

import_or_reload('labscriptlib.RbRb.transport_functions') # to make sure the globals in runmanager are reloaded
from labscriptlib.RbRb.transport_functions import *

import sys # to print warning messages

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

if molasses_cooling_freq_end < molasses_cooling_freq_start:
    message = 'User Warning: Cooling gets less red detuned during molasses!'
    sys.stderr.write(message+'\n')

img_list = [Do_FluoImage, Do_transportImage, Do_AbsImage]    
if np.count_nonzero(img_list)>1:
    message = 'You are multiple types of images!'
    sys.stderr.write(message+'\n')
#)


'''

Sequence

'''

start()
t = 0
Initial_State(t)

t += 0.091 # This time matches the old script for easy comparison

t = MOT_load(t)

if Do_MOT_quad_trap:
    t = CMOT(t)
    print('t='+str(t)+', CMOT done!')
    
    t = molasses(t)
    print('t='+str(t)+', Molasses done!')
    
    # Cooling lock monitor
    do8.go_high(t-OptPump_cooling_lock_time*ms) # Cooling freq starts to change for optical pumping.
    do8.go_low(t) # Cooling freq expected to settle.
    
    t = Opt_Pump(t)
    print('t='+str(t)+', Optical pumping done!')  
    
    t = MOT_cell_quad_trap(t)
    print('t='+str(t)+', MOT cell quad trap done!') 
    shutter_turn_on = True
else:
    shutter_turn_on = False

if Do_transport:
    t = Bidirectional_transport(t)
    
    if Do_inverse_transport:
        t = Bidirectional_transport(t, inverse=True)
    
if Do_evap:  
    t = evap(t)    
    print('t='+str(t)+', evap done!')

t = Imaging_prep(t)

t += TOF*ms
print('t='+str(t)+', TOF done!')

if Do_AbsImage:
    exec("probe_"+probe_direction+"(t,'atom')")
    t += 0.1
    exec("probe_"+probe_direction+"(t,'probe')")
    t += 0.1
    
if Do_FluoImage:
    Fluo_image(t, 'fluo_img', shutter_turn_on=shutter_turn_on)
    t += 0.1
    Fluo_image(t, 'bg') # By default, shutters do not open in this function

Initial_State(t)

if Do_AbsImage or Do_transportImage:
    t += 0.1
    exec("probe_"+probe_direction+"(t,'bg')")
    probe_direction = 'XZ' # used in lyse analysis

# Monitor coil current
coil_current_monitor(0, t)

t += 0.1

print('t='+str(t)+', Experiment done!')
stop(t)
    