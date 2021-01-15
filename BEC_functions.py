from labscript import *
from labscriptlib.common.utils import Limits
from labscriptlib.common.functions import *
from labscript_utils import import_or_reload
sys.path.append(r'C:\Users\RbRb\labscript-suite\userlib\labscriptlib\RbRb')
from coil_config import *

MHz = 1e6
us = 1e-6
ms = 1e-3

def set_bias(start, B_bias):
    x_shim.constant(start, B_bias[0], units='A')
    y_shim.constant(start, B_bias[1], units='A')
    z_shim.constant(start, B_bias[2], units='A')

def Initial_State(t):
# Coils
    coil_ch1.constant(t, -10, units="A") 
    coil_ch2.constant(t, -10, units="A")
    coil_ch3.constant(t, -10, units="A")
    coil_ch4.constant(t, -10, units="A")
    coil_ch1_enable.go_low(t)
    coil_ch2_enable.go_low(t)
    coil_ch3_enable.go_low(t)
    coil_ch4_enable.go_low(t)
    MOT_quad_select(t)   
    outer_coil_1_select(t)
    inner_coil_1_select(t)
    outer_coil_2_select(t)
    
# Lasers
    Cooling.setfreq(t, MOT_cooling_freq)
    Cooling.setamp(t, 1)
    Repump.setfreq(t, MOT_repump_freq)
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
    
    
    
def MOT_load(t, B_bias):
# UV
    if UV_onoff:
        UV.go_high(t)
    UV.go_low(t+MOT_load_time)
# Coils    
    coil_ch1.constant(t, MOT_quad_curr, units="A")
    coil_ch1_enable.go_high(t-1*ms) 
    MOT_quad_select(t)
    set_bias(t, B_bias)
# Lasers    
    Cooling.setfreq(t, MOT_cooling_freq)
    Cooling.setamp(t, 1)
    Repump.setfreq(t, MOT_repump_freq)
    Repump.setamp(t, 1)
    
    Cooling_AOM.go_high(t)
    Cooling_int.constant(t, MOT_cooling_int, units="Vs")
    Cooling_shutter.open(t)
    
    Repump_AOM.go_high(t)
    Repump_int.constant(t, MOT_repump_int, units="Vs")
    Repump_shutter.open(t)   

    return t + MOT_load_time   

def Imaging_prep(t):
   
    # Coils
    coil_ch1.constant(t, -10, units="A") 
    coil_ch2.constant(t, -10, units="A")
    coil_ch3.constant(t, -10, units="A")
    coil_ch4.constant(t, -10, units="A")
    coil_ch1_enable.go_low(t)
    coil_ch2_enable.go_low(t)
    coil_ch3_enable.go_low(t)
    coil_ch4_enable.go_low(t)
    
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
    UV.go_low(t)
    
    evap_switch.go_low(t)
    evap_int.constant(t, 0)
    return t
    
def Fluo_image(t, duration, frametype):
    set_bias(t-TOF, np.array([0,0,0]))
    
    Cooling.setfreq(t-MOT_cooling_lock_time, Fluo_cooling_freq)
    Cooling_AOM.go_high(t)
    Cooling_int.constant(t, MOT_cooling_int)
    Cooling_shutter.go_high(t-MOT_cooling_lock_time*1)
    
    Repump.setfreq(t, MOT_repump_freq)
    Repump_AOM.go_high(t)
    Repump_int.constant(t, MOT_repump_int)
    Repump_shutter.go_high(t-MOT_cooling_lock_time*1)
    
    MOT_YZ_flea.expose(t-0.01*ms,'fluo_img', trigger_duration=duration+0.01*ms, frametype=frametype)
    return t+duration

  
    
# def subDoppler(t, duration, freq_c_s, freq_c_e, B_bias):
    # t1_enable.go_low(t)
    # self.set_bias(t, B_bias) # IBS: should be optimized (critical) done
    # Cooling.frequency.customramp(t, duration-opt_adv, LineRamp, freq_c_s, freq_c_e, samplerate=1/mol_freq_step) # IBS: timing code is future bug. 
    # Cool_int.constant(t, mol_cool_int)
    # # Repump_int.constant(start, mol_rep_int_end)
    # Repump_int.customramp(t, duration, LineRamp, mol_rep_int_start, mol_rep_int_end, samplerate=1/mol_freq_step)
    # return t + duration

# def opt_pump(t, duration):
    # Shutter_Opt_pumping.open(t) # Note: this is due to the minimum exposure 5ms of SR475, move to PG cooling.
    # Cooling_AOM.go_low(t-opt_adv)
    # Cool_int.constant(t, cool_z)
    # set_freq(Cooling, t-opt_adv, res+opt_f*MHz)
    # # IAN: Repump power matters here
    # OptPump_AOM.go_high(t)
    # OptPump_AOM.go_low(t+duration)
    # OptPump_int.constant(t, OptPumpint)
    # OptPump_int.constant(t+duration, opt_z)
    # Repump_int.constant(t, opt_rep_int)
    # Repump_AOM.go_low(t+duration)
    # Repump_int.constant(t+duration, rep_z)
    # self.set_bias(t-0.5*ms, np.array(B_bias_optpump)) # IAN: How fast does bias actually change? (Field)
    # return t+duration

if __name__ == '__main__':
	start()
	stop(1)    