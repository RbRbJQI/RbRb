from labscript import *
from labscriptlib.common.utils import Limits
from labscriptlib.common.functions import *
from labscript_utils import import_or_reload
sys.path.append(r'C:\Users\RbRb\labscript-suite\userlib\labscriptlib\RbRb')


MHz = 1e6
us = 1e-6
ms = 1e-3

'''
General functions

'''
#(
# Override the "shutter" class "close" method
class our_Shutter(Shutter):
    def __init__(self, *args, **kwargs):
        Shutter.__init__(self, *args, **kwargs)

    def close(self, t):
        if not Keep_warm:
            Shutter.close(self, t)
        else:
            Shutter.open(self, t)

            
def set_bias(t, B_bias):
    x_shim.constant(t, B_bias[0], units='A')
    y_shim.constant(t, B_bias[1], units='A')
    z_shim.constant(t, B_bias[2], units='A')

def set_science_bias(t, B_bias):
    Science_Bias_x.constant(t, B_bias[0], units="A")

#)

'''
Coil configuration functions
This list is copied from current.py
'''
#(
# From MOT to science cell, coil number increases, e.g., outer_coil_1 is closest to the MOT cell.
#                          00                 10            01           11
# coil group 0 includes:  MOT_quad       inner_coil_2   inner_coil_4   
# coil group 1 includes:  outer_coil_1   outer_coil_3                   
# coil_group 2 includes:  inner_coil_1   inner_coil_3   outer_coil_5
# coil_group 3 includes:  outer_coil_2   outer_coil_4   science_quad

def All_coil_off(t):
    coil_ch0.constant(t, -10, units="A") 
    coil_ch1.constant(t, -10, units="A")
    coil_ch2.constant(t, -10, units="A")
    coil_ch3.constant(t, -10, units="A")
    coil_ch0_enable.go_low(t)
    coil_ch1_enable.go_low(t)
    coil_ch2_enable.go_low(t)
    coil_ch3_enable.go_low(t)

def MOT_quad_select(t):
    coil_ch0_0.go_low(t)
    coil_ch0_1.go_low(t)  
    
def outer_coil_1_select(t):
    coil_ch1_0.go_low(t)
    coil_ch1_1.go_low(t)

def inner_coil_1_select(t):
    coil_ch2_0.go_low(t)
    coil_ch2_1.go_low(t)

def outer_coil_2_select(t):
    coil_ch3_0.go_low(t)
    coil_ch3_1.go_low(t)

MOT_quad_ch = 'coil_ch0'
#)
'''

Experimental stages


'''
#(
def Initial_State(t):
# Coils
    All_coil_off(t)
    MOT_quad_select(t)   
    outer_coil_1_select(t)
    inner_coil_1_select(t)
    outer_coil_2_select(t)
    set_science_bias(t, [0,0,0])
    Science_Bias_y.constant(t, 0, units="A")
    set_bias(t, [MOT_B_bias_x*0,MOT_B_bias_y*0,MOT_B_bias_z*0]) 
    
# Lasers
    Cooling.setfreq(t, MOT_cooling_freq*MHz)
    Cooling.setamp(t, 1)
    Repump.setfreq(t, MOT_repump_freq*MHz)
    Repump.setamp(t, 1)

    Probe_AOM.go_low(t)
    Probe_int.constant(t, 0, units="Vs")
    Probe_shutter.close(t)
    
    Cooling_AOM.go_low(t)
    Cooling_int.constant(t, 0, units="Vs")
    Cooling_shutter.close(t)
    
    Repump_AOM.go_low(t)
    Repump_int.constant(t, 0, units="Vs")
    Repump_shutter.close(t)
    
    OptPump_AOM.go_low(t)
    OptPump_int.constant(t, 0, units="Vs")
    OptPump_shutter.close(t)  

    Repump_science_int.constant(t, 0, units="Vs")
    Repump_science_shutter.close(t)   

# Other    
    UV.go_low(t)
    
    evap_switch.go_low(t)
    evap_int.constant(t, 0)
          
def MOT_load(t):
# UV
    if UV_onoff:
        UV.go_high(t)
        UV.go_low(t+MOT_load_time)
# Coils    
    # MOT quad is selected in Initial_State
    exec(MOT_quad_ch + "_enable.go_high(t-1*ms)")
    exec(MOT_quad_ch + ".constant(t, MOT_quad_curr, units='A')")     
    set_bias(t, np.array([MOT_B_bias_x,MOT_B_bias_y, MOT_B_bias_z]))
# Lasers    
    Cooling.setfreq(t, MOT_cooling_freq*MHz)
    Cooling.setamp(t, 1)
    Repump.setfreq(t, MOT_repump_freq*MHz)
    Repump.setamp(t, 1)
    
    Cooling_AOM.go_high(t)
    Cooling_int.constant(t, MOT_cooling_int, units="Vs")
    Cooling_shutter.open(t)
    
    Repump_AOM.go_high(t)
    Repump_int.constant(t, MOT_repump_int, units="Vs")
    Repump_shutter.open(t) 

    return t + MOT_load_time   

def CMOT(t):
# Coils
    sample_rate=1/(0.5*ms)
    
    # Pass dynamic globals
    CMOT_quad_curr_start = MOT_quad_curr
    CMOT_B_bias_start = np.array([MOT_B_bias_x,MOT_B_bias_y, MOT_B_bias_z])
    CMOT_B_bias_end = np.array([CMOT_B_bias_end_x,CMOT_B_bias_end_y,CMOT_B_bias_end_z])
    CMOT_cooling_freq_start = MOT_cooling_freq
    
    exec(MOT_quad_ch + ".customramp(t, CMOT_duration*ms, HalfGaussRamp, CMOT_quad_curr_start, CMOT_quad_curr_end, CMOT_duration*ms, samplerate=sample_rate, units='A')")
    x_shim.customramp(t, CMOT_duration*ms, HalfGaussRamp, CMOT_B_bias_start[0], CMOT_B_bias_end[0], CMOT_duration*ms, samplerate=sample_rate, units='A')
    y_shim.customramp(t, CMOT_duration*ms, HalfGaussRamp, CMOT_B_bias_start[1], CMOT_B_bias_end[1], CMOT_duration*ms, samplerate=sample_rate, units='A')
    z_shim.customramp(t, CMOT_duration*ms, HalfGaussRamp, CMOT_B_bias_start[2], CMOT_B_bias_end[2], CMOT_duration*ms, samplerate=sample_rate, units='A')      
# Lasers
    Cooling.frequency.customramp(t, CMOT_duration*ms, HalfGaussRamp, CMOT_cooling_freq_start*MHz, CMOT_cooling_freq_end*MHz, CMOT_duration*ms, samplerate=sample_rate) 
    Cooling_int.constant(t, CMOT_cooling_int, units="Vs") 
    Repump_int.constant(t, CMOT_repump_int, units="Vs") 
    return t + CMOT_duration*ms


def molasses(t):
# Coils
    exec(MOT_quad_ch + "_enable.go_low(t)")
    exec(MOT_quad_ch + ".constant(t, -10, units='A')")
    set_bias(t, np.array([B_zero_x,B_zero_y,B_zero_z])) 
# Lasers
    sample_rate=1/(0.2*ms)
    Cooling.frequency.customramp(t, molasses_duration*ms-OptPump_cooling_lock_time*ms, LineRamp, molasses_cooling_freq_start*MHz, molasses_cooling_freq_end*MHz, samplerate=sample_rate) 
    Cooling_int.customramp(t, molasses_duration*ms, LineRamp, molasses_cooling_int_start, molasses_cooling_int_end, samplerate=sample_rate, units="Vs")
    Repump_int.customramp(t, molasses_duration*ms, LineRamp, molasses_repump_int_start, molasses_repump_int_end, samplerate=sample_rate, units="Vs")
    return t + molasses_duration*ms

def Opt_Pump(t):
# Coils 
    set_bias(t-B_bias_respond_time*ms, np.array([OptPump_B_bias_x,OptPump_B_bias_y,OptPump_B_bias_z]))
 
# Lasers
    # Cooling light is turned off in advance. At the end of molasses, only repump is on when B bias starts to change or the cooling laser freq starts to change. The time scale is ~2ms.
    Cooling_AOM.go_low(t-max(B_bias_respond_time*ms,OptPump_cooling_lock_time*ms)) 
    Cooling_int.constant(t, 0, units="Vs")
    Cooling.setfreq(t-OptPump_cooling_lock_time*ms, OptPump_cooling_freq*MHz) # Cooling freq ramp finishes OptPump_cooling_lock_time*ms before molasses finish. The starting time here matches the molasses stage.
    
    OptPump_shutter.open(t) 
    OptPump_AOM.go_high(t)
    OptPump_int.constant(t, OptPump_OptPump_int, units="Vs")  
    Repump_int.constant(t, OptPump_repump_int, units="Vs")
    
    OptPump_AOM.go_low(t+OptPump_duration*ms)
    OptPump_int.constant(t+OptPump_duration*ms, 0, units="Vs")
    Repump_AOM.go_low(t+OptPump_duration*ms)
    Repump_int.constant(t+OptPump_duration*ms, 0, units="Vs")
    
    return t + OptPump_duration*ms
    
def MOT_cell_quad_trap(t):
    # add 10 ms here because of optical pumping.
    # TTL/analog of OptPump and Repump are turned off at the end of optical pumping stage.
    Cooling_shutter.close(t+10*ms)
    Repump_shutter.close(t+10*ms)  
    Probe_shutter.close(t+10*ms)
    OptPump_shutter.close(t+10*ms) 
    
    # Set cooling laser frequency for imaging
    if Do_FluoImage:
        Cooling.setfreq(t+10*ms, FluoImage_cooling_freq*MHz) 
    elif Do_AbsImage or Do_transportImage:
        exec("Cooling.setfreq(t+10*ms, probe_" + probe_direction + "_cooling_freq*MHz)")  
    
    # start turning on quad coils at the end of optical pumping
    exec(MOT_quad_ch + "_enable.go_high(t-0.1*ms)")
    exec(MOT_quad_ch + ".constant(t-0.2*ms, quad_trap_quad_curr_start, units='A')")     
       
    quad_trap_B_bias_start = np.array([quad_trap_B_bias_start_x,quad_trap_B_bias_start_y,quad_trap_B_bias_start_z])
    x_shim.constant(t, quad_trap_B_bias_start[0], units='A') 
    y_shim.constant(t, quad_trap_B_bias_start[1], units='A')
    z_shim.constant(t, quad_trap_B_bias_start[2], units='A')
    
    # Compress the trap
    sample_rate=1/(0.2*ms)   
    exec(MOT_quad_ch + ".customramp(t+quad_trap_quad_ramp_start_delay*ms, quad_trap_ramp_duration*ms, LineRamp, quad_trap_quad_curr_start, quad_trap_quad_curr_end, samplerate=sample_rate, units='A')")       

    quad_trap_B_bias_end = np.array([quad_trap_B_bias_end_x,quad_trap_B_bias_end_y,quad_trap_B_bias_end_z])
    x_shim.customramp(t+quad_trap_quad_ramp_start_delay*ms, quad_trap_ramp_duration*ms, LineRamp, quad_trap_B_bias_start[0], quad_trap_B_bias_end[0], samplerate=sample_rate, units='A')  
    y_shim.customramp(t+quad_trap_quad_ramp_start_delay*ms, quad_trap_ramp_duration*ms, LineRamp, quad_trap_B_bias_start[1], quad_trap_B_bias_end[1], samplerate=sample_rate, units='A')
    z_shim.customramp(t+quad_trap_quad_ramp_start_delay*ms, quad_trap_ramp_duration*ms, LineRamp, quad_trap_B_bias_start[2], quad_trap_B_bias_end[2], samplerate=sample_rate, units='A')
    
    return t + quad_trap_quad_ramp_start_delay*ms + quad_trap_ramp_duration*ms + quad_trap_hold_time*ms
    
def evap(t):
    # RF
    evap_switch.go_high(t)
    evap_int.constant(t, evap_int_saturation) 
    evap_rf.setamp(t, evap_rf_Novatech_amp) 
    
    # Coils
    evap_rf.frequency.customramp(t, evap_duration, LineRamp, evap_rf_freq_start*MHz, evap_rf_freq_end*MHz, samplerate = 1/(evap_step_size*ms))
    
    evap_switch.go_low(t+evap_duration)
    evap_int.constant(t+evap_duration, 0)
    evap_rf.setamp(t+evap_duration, 0)
    
    return t + evap_duration
#)

'''

Imaging

'''    
#(
def Imaging_prep(t): 
    # Coils
    All_coil_off(t)
        
    if Do_FluoImage:
        set_bias(t, [0,0,0]) 
    elif Do_AbsImage or Do_transportImage:
        if probe_direction == 'science':
            set_bias(t, [0,0,0]) 
            set_science_bias(t, [probe_science_B_bias_x,0,0])
            Repump.setfreq(t, probe_science_repump_freq*MHz)
        else:
            exec("set_bias(t, probe_" + probe_direction + "_B_bias)")
                        
    # Lasers
    Probe_AOM.go_low(t)
    Probe_int.constant(t, 0, units="Vs")
    
    Cooling_AOM.go_low(t)
    Cooling_int.constant(t, 0, units="Vs")
    
    Repump_AOM.go_low(t)
    Repump_int.constant(t, 0, units="Vs")
    
    OptPump_AOM.go_low(t)
    OptPump_int.constant(t, 0, units="Vs") 
    
    return t

def Fluo_image(t, frametype, shutter_turn_on=False):
    if not frametype=='bg':       
        Cooling.setfreq(t-cooling_lock_time*ms, FluoImage_cooling_freq*MHz)
        Cooling_AOM.go_high(t)
        Cooling_int.constant(t, FluoImage_cooling_int, units="Vs")

        Repump.setfreq(t, FluoImage_repump_freq*MHz)
        Repump_AOM.go_high(t)
        Repump_int.constant(t, FluoImage_repump_int, units="Vs")      
 
        if shutter_turn_on:
            Cooling_shutter.open(t)
            Repump_shutter.open(t)
        
    MOT_XZ_flea.expose(t-0.01*ms,'fluo_img', trigger_duration=FluoImage_duration*ms+0.01*ms, frametype=frametype)
    return t+FluoImage_duration*ms

def probe_XZ(t, frametype):
    if not frametype=='bg':
        Cooling.setfreq(t-cooling_lock_time*ms, probe_XZ_cooling_freq*MHz)
        Probe_int.constant(t, probe_XZ_int, units="Vs")
        Probe_AOM.go_high(t)
        Probe_shutter.open(t)

        Repump_AOM.go_high(t)
        Repump_int.constant(t, probe_XZ_repump_int, units="Vs")  

        Probe_AOM.go_low(t+probe_XZ_duration*ms)
        Probe_int.constant(t+probe_XZ_duration*ms, 0, units="Vs")  
        
    MOT_XZ_flea.expose(t-0.01*ms,'abs_img', trigger_duration=probe_XZ_duration*ms+0.01*ms, frametype=frametype) 
    
def probe_XY(t, frametype):
    if not frametype=='bg':
        Cooling.setfreq(t-cooling_lock_time*ms, probe_XY_cooling_freq*MHz)
        OptPump_int.constant(t, probe_XY_int, units="Vs")
        OptPump_AOM.go_high(t)
        OptPump_shutter.open(t)

        Repump_AOM.go_high(t)
        Repump_int.constant(t, probe_XZ_repump_int, units="Vs")  
        
        OptPump_AOM.go_low(t+probe_XY_duration*ms)
        OptPump_int.constant(t+probe_XY_duration*ms, 0, units="Vs")  
        
    MOT_XY_flea.expose(t-0.01*ms,'abs_img', trigger_duration=probe_XY_duration*ms+0.01*ms, frametype=frametype) 
    
def probe_science(t, frametype):# science cell absorption imaging
    if not frametype=='bg':
        Cooling.setfreq(t-cooling_lock_time*ms, probe_science_cooling_freq*MHz)
        Probe_int.constant(t, probe_science_int, units="Vs") 
        Probe_AOM.go_high(t)        
        Probe_shutter.open(t)               
        
        Repump_science_int.constant(t, probe_science_repump_int, units="Vs")
        Repump_science_shutter.open(t) 
        
        Probe_AOM.go_low(t+probe_science_duration*ms)
        Probe_int.constant(t+probe_science_duration*ms, 0, units="Vs")  
        
    Science_flea.expose(t-0.01*ms,'abs_img', trigger_duration=probe_science_duration*ms+0.01*ms, frametype=frametype)
#)

'''

Debugging functions

'''    
#(
def coil_current_monitor(start, end):
    testin0.acquire('curr0', start, end)
    testin1.acquire('curr1', start, end)
    testin2.acquire('curr2', start, end)    
    testin3.acquire('curr3', start, end)    
    testin4.acquire('fluo', start, end)
    testin5.acquire('biasx', start, end)
    testin6.acquire('biasy', start, end)
    Repump_monitor.acquire('Repump_monitor', start, end)
    Cooling_monitor.acquire('Cooling_monitor', start, end)
    return 'Collected as fluo'
#)

    
if __name__ == '__main__':
	start()
	stop(1)    