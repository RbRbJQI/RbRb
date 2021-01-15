from labscript import *
from labscriptlib.common.utils import Limits
from labscriptlib.common.functions import *
from labscript_utils import import_or_reload

MHz = 1e6
us = 1e-6
ms = 1e-3

import_or_reload('labscriptlib.RbRb.transport.new_transport_optimisation')
from labscriptlib.RbRb.transport.new_transport_optimisation import transport
class current_switch:
    def __init__(self, time_t0_on, time_t0_off, time_t1_on, time_t1_off, time_te_on, time_te_off):
        self.time_t0_on = time_t0_on
        self.time_t0_off = time_t0_off
        self.time_t1_on = time_t1_on
        self.time_t1_off = time_t1_off
        self.time_te_on = time_te_on
        self.time_te_off = time_te_off
        
def Channel_n(n):
    if n==0:
        return 4#biasx, t_biasx
    if n in [1,5,9]:
        return 0#curr0, t0
    if n in [2,6]:
        return 1#curr1, t1
    if n in [3,7,10]:
        return 2#curr2, t2
    if n in [4,8,11]:
        return 3#np.array(curr3), t3

def Initial_State(t):
    quad_MOT.constant(t, 1)
    transport1.constant(t, 1)
    transport2.constant(t, 1)
    transport3.constant(t, 1)
    t1_0.go_low(t)
    t1_1.go_low(t)
    t2_0.go_low(t)
    t2_1.go_low(t)
    t3_0.go_low(t)
    t3_1.go_low(t)
    t4_0.go_low(t)
    t4_1.go_low(t)
    Cooling.setfreq(t, MOT_cooling_freq)
    Cooling.setamp(t, 1)
    Repump.setfreq(t, MOT_repump_freq)
    Repump.setamp(t, 1)
    evap_switch.go_low(t)
    evap_int.constant(t, 0)
    # self.t_t, self.t_I = [], [] What are they?
    MOT_Probe_AOM.go_low(t)
    Probe_int.constant(t, 0, units="Vs")
    Cooling_AOM.go_low(t)
    Repump_AOM.go_low(t)
    OptPump_AOM.go_low(t)
    UV.go_low(t)
    Shutter_Cooling.close(t)
    Shutter_Repump.close(t)
    Shutter_Opt_pumping.close(t)
    Shutter_Probe.close(t)       

def MOT_load(t, load_time, B_bias, quad_curr, UV_onoff):
    if UV_onoff:
        UV.go_high(t)
    UV.go_low(t+min(load_time,dur_UV))
    t1_enable.go_high(t-1*ms) # What is it?
    quad_MOT.constant(t, value=quad_curr)
    Cooling.setfreq(t, MOT_cooling_freq)
    Cooling.setamp(t, 1)
    Repump.setfreq(t, MOT_repump_freq)
    Repump.setamp(t, 1)
    Cooling_AOM.go_high(t)
    Repump_AOM.go_high(t)
    set_bias(t, B_bias)
    Cool_int.constant(t, MOT_cooling_int) # IBS: should be optimized, and set so 0 is 0
    Repump_int.constant(t, MOT_repump_int)# IBS: should be optimized, and set so 0 is 0
    Shutter_Cooling.open(t)
    Shutter_Repump.open(t)
    Shutter_Opt_pumping.open(t) # Note: this is due to the minimum exposure 5ms of SR475, move to PG cooling.
    t += load_time
    return t   

def MOT_deload(start):
    B_bias_mol = (0,0,B_bias_mol_z)
    UV.go_low(start)
    Cooling_AOM.go_low(start)
    Repump_AOM.go_low(start)
    OptPump_AOM.go_low(start)
    Cool_int.constant(start, 0, units='Vs')
    Repump_int.constant(start, 0, units='Vs')
    OptPump_int.constant(start, 0, units='Vs')
    Shutter_Cooling.close(start)
    Shutter_Repump.close(start)
    quad_MOT.constant(start,1)
    transport1.constant(start,1)
    transport2.constant(start,1)
    transport3.constant(start,1)
    t1_enable.go_low(start)
    t2_enable.go_low(start)
    t3_enable.go_low(start)
    t4_enable.go_low(start)
    set_bias(start, B_bias_mol) # Dont want to do this!  Want to go to "true zero"
    # Where to find preset "true zero"?
    return start
    
def Fluo_image(start, duration, frametype):
    Cooling.setfreq(start-MOT_cooling_lock_time, Fluo_cooling_freq)
    Cooling_AOM.go_high(start)
    Cool_int.constant(start, MOT_cooling_int)
    Repump_AOM.go_high(start)
    Repump_int.constant(start, MOT_repump_int)
    Shutter_Cooling.go_high(start-MOT_cooling_lock_time*6.5)
    Shutter_Repump.go_high(start-MOT_cooling_lock_time*1)
    MOT_YZ_flea.expose(start-0.01*ms,'fluo_img', trigger_duration=duration+0.01*ms, frametype=frametype)
    return start+duration

def set_bias(start, B_bias):
    x_shim.constant(start, B_bias[0], units='A')
    y_shim.constant(start, B_bias[1], units='A')
    z_shim.constant(start, B_bias[2], units='A')    