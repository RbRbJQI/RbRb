from labscript import *
from labscriptlib.common.utils import Limits
from labscriptlib.common.functions import *
from labscript_utils import import_or_reload
sys.path.append(r'C:\Users\RbRb\labscript-suite\userlib\labscriptlib\RbRb')
from coil_config import *

MHz = 1e6
us = 1e-6
ms = 1e-3

'''
General functions

'''
#(
def set_bias(start, B_bias):
    x_shim.constant(start, B_bias[0], units='A')
    y_shim.constant(start, B_bias[1], units='A')
    z_shim.constant(start, B_bias[2], units='A')
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
    set_bias(t, np.array([B_zero_x,B_zero_y,B_zero_z])) 
# Lasers
    sample_rate=1/(0.2*ms)
    Cooling.frequency.customramp(t, molasses_duration*ms-molasses_cooling_lock_time*ms, LineRamp, molasses_cooling_freq_start*MHz, molasses_cooling_freq_end*MHz, samplerate=sample_rate) 
    Cooling_int.constant(t, molasses_cooling_int, units="Vs")
    Repump_int.customramp(t, molasses_duration*ms, LineRamp, molasses_repump_int_start, molasses_repump_int_end, samplerate=sample_rate, units="Vs")
    return t + molasses_duration*ms

def Opt_Pump(t):
# Coils 
    set_bias(t-B_bias_respond_time*ms, np.array([OptPump_B_bias_x,OptPump_B_bias_y,OptPump_B_bias_z]))
 
# Lasers
    # Cooling light is turned off in advance. At the end of molasses, only repump is on when B bias starts to change or the cooling laser freq starts to change. The time scale is ~2ms.
    Cooling_AOM.go_low(t-max(B_bias_respond_time*ms,OptPump_cooling_lock_time*ms)) 
    Cooling_int.constant(t, 0, units="Vs")
    Cooling.setfreq(t-OptPump_cooling_lock_time*ms, OptPump_cooling_freq*MHz)
    
    OptPump_shutter.open(t-5*ms) # minimum exposure 5ms of SR475
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
    elif Do_AbsImage:
        Cooling.setfreq(t+10*ms, AbsImage_cooling_freq*MHz)  
    
    # start turning on quad coils at the end of optical pumping
    exec(MOT_quad_ch + "_enable.go_high(t-0.1*ms)")
    exec(MOT_quad_ch + ".constant(t-0.2*ms, quad_trap_quad_curr_start, units='A')")     
    
    # Move the atoms to the desired position
    sample_rate=1/(0.2*ms)
    
    # Pass dynamic globals  
    quad_trap_B_bias_start = np.array([B_zero_x,B_zero_y,B_zero_z]) # The starting bias is the same as in molasses.
    quad_trap_B_bias_middle = np.array([quad_trap_B_bias_middle_x,quad_trap_B_bias_middle_y,quad_trap_B_bias_middle_z])
    
    x_shim.customramp(t, quad_trap_B_bias_ramp_duration*ms, LineRamp, quad_trap_B_bias_start[0], quad_trap_B_bias_middle[0], samplerate=sample_rate, units='A') 
    y_shim.customramp(t, quad_trap_B_bias_ramp_duration*ms, LineRamp, quad_trap_B_bias_start[1], quad_trap_B_bias_middle[1], samplerate=sample_rate, units='A')
    z_shim.customramp(t, quad_trap_B_bias_ramp_duration*ms, LineRamp, quad_trap_B_bias_start[2], quad_trap_B_bias_middle[2], samplerate=sample_rate, units='A')
    
    # Compress the trap
    sample_rate=1/(0.5*ms)   
    exec(MOT_quad_ch + ".customramp(t+quad_trap_quad_ramp_start_delay*ms, quad_trap_quad_ramp_duration*ms, LineRamp, quad_trap_quad_curr_start, quad_trap_quad_curr_end, samplerate=sample_rate, units='A')")       

    sample_rate=1/(0.2*ms)
    quad_trap_B_bias_end = np.array([quad_trap_B_bias_end_x,quad_trap_B_bias_end_y,quad_trap_B_bias_end_z])
    x_shim.customramp(t+quad_trap_quad_ramp_start_delay*ms, quad_trap_B_bias_ramp_duration*ms, LineRamp, quad_trap_B_bias_middle[0], quad_trap_B_bias_end[0], samplerate=sample_rate, units='A')  
    y_shim.customramp(t+quad_trap_quad_ramp_start_delay*ms, quad_trap_B_bias_ramp_duration*ms, LineRamp, quad_trap_B_bias_middle[1], quad_trap_B_bias_end[1], samplerate=sample_rate, units='A')
    z_shim.customramp(t+quad_trap_quad_ramp_start_delay*ms, quad_trap_B_bias_ramp_duration*ms, LineRamp, quad_trap_B_bias_middle[2], quad_trap_B_bias_end[2], samplerate=sample_rate, units='A')
    
    return t + quad_trap_quad_ramp_start_delay*ms + quad_trap_quad_ramp_duration*ms + quad_trap_hold_time*ms
#)

'''

Imaging

'''    
#(
def Imaging_prep(t): 
    # Coils
    All_coil_off(t)
    
    if Do_FluoImage:
        # Pass dynamic globals  
        B_zero = np.array([B_zero_x,B_zero_y,B_zero_z])
        set_bias(t, B_zero) 
    elif Do_AbsImage:
        set_bias(t, AbsImage_B_Bias)
    
    # Lasers
    Probe_AOM.go_low(t)
    Probe_int.constant(t, 0, units="Vs")
    
    Cooling_AOM.go_low(t)
    Cooling_int.constant(t, 0, units="Vs")
    
    Repump_AOM.go_low(t)
    Repump_int.constant(t, 0, units="Vs")
    
    OptPump_AOM.go_low(t)
    OptPump_int.constant(t, 0, units="Vs") 
    
    # Others    
    evap_switch.go_low(t)
    evap_int.constant(t, 0)
    return t

def Fluo_image(t, frametype, shutter_turn_on=False):
    if not frametype=='bg':       
        # Pass dynamic globals
        FluoImage_cooling_int = MOT_cooling_int
        FluoImage_repump_int = MOT_repump_int
        FluoImage_repump_freq = MOT_repump_freq

        Cooling.setfreq(t-cooling_lock_time*ms, FluoImage_cooling_freq*MHz)
        Cooling_AOM.go_high(t)
        Cooling_int.constant(t, FluoImage_cooling_int, units="Vs")

        Repump.setfreq(t, FluoImage_repump_freq*MHz)
        Repump_AOM.go_high(t)
        Repump_int.constant(t, FluoImage_repump_int, units="Vs")      
 
        if shutter_turn_on:
            Cooling_shutter.open(t)
            Repump_shutter.open(t)
        
    MOT_YZ_flea.expose(t-0.01*ms,'fluo_img', trigger_duration=FluoImage_duration*ms+0.01*ms, frametype=frametype)
    return t+FluoImage_duration*ms
#)

    
if __name__ == '__main__':
	start()
	stop(1)    