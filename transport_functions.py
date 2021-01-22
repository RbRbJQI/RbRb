from labscript import *
from labscriptlib.common.utils import Limits
from labscriptlib.common.functions import *
from labscript_utils import import_or_reload
sys.path.append(r'C:\Users\RbRb\labscript-suite\userlib\labscriptlib\RbRb')

import_or_reload('labscriptlib.RbRb.transport.new_transport_optimisation') # to make sure the globals in runmanager are reloaded
from labscriptlib.RbRb.transport.new_transport_optimisation import transport

MHz = 1e6
us = 1e-6
ms = 1e-3

class current_switch(object):
    def __init__(self, time_t0_on, time_t0_off, time_t1_on, time_t1_off, time_te_on, time_te_off):
        self.time_t0_on = time_t0_on
        self.time_t0_off = time_t0_off
        self.time_t1_on = time_t1_on
        self.time_t1_off = time_t1_off
        self.time_te_on = time_te_on
        self.time_te_off = time_te_off

def Bidirectional_transport(t, inverse=False):
    from scipy.interpolate import interp1d
    transport_time_list = np.arange(0, transport_duration, transport_step_size*ms)
    I_coils = transport.currents_at_time(transport_time_list) # Only need the time list as input. The sequence is pre-programmed.

    if inverse:
        I_coils = np.array([np.flip(I_coil) for I_coil in I_coils])
    
    if Do_transportImage:   
        probe_transport_in_progess(t, ind_probe_coils, I_coils)
    
    I_channels = np.zeros((tot_ch,len(transport_time_list)))
    curr_ratio=[curr_ratio_ch1, curr_ratio_ch2, curr_ratio_ch3, curr_ratio_ch4]
    
    for ch in range(tot_ch):
        I_channels[ch,:] = transport.currents_for_channel(transport_time_list, transport_duration, ch+1, ratio=curr_ratio[ch], I_coils=I_coils) 
    I_channels_interp = [interp1d(transport_time_list, I_channels[ch,:], 'cubic', fill_value='extrapolate') for ch in range(tot_ch)]
    
    '''
    coil_order_in_I_coils = ['push_coil', 'MOT_quad', 'outer_coil_1', 'inner_coil_1', 'outer_coil_2', 'inner_coil_2', 
                            'outer_coil_3', 'inner_coil_3', 'outer_coil_4', 'inner_coil_4', 'outer_coil_5', 'science_quad']
    
    This list is copied from current.py
    '''
    if not Do_transport_shim_coil: # No transport shim coil
        channel_order_in_I_coils = [4, 0, 1, 2, 3, 0, 
                                1, 2, 3, 0, 2, 3]
        ch0_order_in_I_coils = ['', 'off', 'off', 'off', 'off', 'on', 
                                'on', 'on', 'on', 'off', 'off', 'off']
        ch1_order_in_I_coils = ['', 'off', 'off', 'off', 'off', 'off', 
                                'off', 'off', 'off', 'on', 'on', 'on']
    else: # Add transport shim coils
        channel_order_in_I_coils = [4, 0, 1, 2, 3, 0, 
                                    1, 2, 3, 0, 2, 3, 
                                    0, 1] #shims
        ch0_order_in_I_coils = ['', 'off', 'off', 'off', 'off', 'on', 
                                    'on', 'on', 'on', 'off', 'off', 'off',
                                    'on', 'on'] #shims
        ch1_order_in_I_coils = ['', 'off', 'off', 'off', 'off', 'off', 
                                    'off', 'off', 'off', 'on', 'on', 'on', 
                                    'on', 'on'] #shims
                                     
        num_shim = len(channel_order_in_I_coils) - 12
        I_coils_shim = np.zeros((num_shim, len(I_coils[0])))
        for shim_ind in range(num_shim):
            start, end = eval( 'transport_shim'+str(shim_ind)+'_start*len(I_coils[0])' ), eval( 'transport_shim'+str(shim_ind)+'_end*len(I_coils[0])' )
            transport_shim_curr  = eval('transport_shim'+str(shim_ind)+'_curr')
            I_coils_shim[shim_ind, round(start):round(end)] = transport_shim_curr
            ramp_dur = transport_shim_ramp_dur
            # #ramp up
            # start_ramp, end_ramp = start, start+int(ramp_dur*len(I_coils[0]))
            # t_ramp = np.arange(0, end_ramp-start_ramp)
            # I_coils_shim[shim_ind, round(start_ramp):round(end_ramp)] = t_ramp/(end_ramp-start_ramp)* transport_shim_curr
            # #ramp down
            # start_ramp, end_ramp = end-int(ramp_dur*len(I_coils[0])), end
            # t_ramp = np.arange(0, end_ramp-start_ramp)
            # I_coils_shim[shim_ind, round(start_ramp):round(end_ramp)] = transport_shim_curr* (1-t_ramp/(end_ramp-start_ramp))
            if inverse:
                I_coils_shim[shim_ind] = np.array(np.flip(I_coils_shim[shim_ind]))
        I_coils = np.vstack((I_coils, I_coils_shim))
        collision_check = eval("I_channels["+str(channel_order_in_I_coils[-num_shim:])+",:]*I_coils_shim")
        if np.sum(collision_check)!=0:
            raise Exception('Transport coil current conflicts!')
        exec("I_channels["+str(channel_order_in_I_coils[-num_shim:])+",:] += I_coils_shim")
        I_channels_interp = [interp1d(transport_time_list, I_channels[ch,:], 'cubic', fill_value='extrapolate') for ch in range(tot_ch)]
        
    switch = [current_switch([],[],[],[],[],[]) for ch in range(tot_ch)]
    for coil in range(1,len(I_coils)):
        # Assuming:
            # 1. No negative current
            # 2. Each coil only turns on once
        coil_in_use_time_list = transport_time_list[np.argwhere(I_coils[coil]>0)] 
        if len(coil_in_use_time_list)>0:
            start = coil_in_use_time_list[0][0] # This is a matrix of size N(time list) x 1
            switch[channel_order_in_I_coils[coil]].time_te_on.append(start)
            exec("switch[channel_order_in_I_coils[coil]].time_t0_"+str(ch0_order_in_I_coils[coil])+".append(start)")
            exec("switch[channel_order_in_I_coils[coil]].time_t1_"+str(ch1_order_in_I_coils[coil])+".append(start)")
    
    for ch in range(tot_ch):
        for time in switch[ch].time_t0_on:
            exec("coil_ch"+str(ch)+"_0.go_high("+str(t+time)+")")
        for time in switch[ch].time_t0_off:
            exec("coil_ch"+str(ch)+"_0.go_low("+str(t+time)+")")
        for time in switch[ch].time_t1_on:
            exec("coil_ch"+str(ch)+"_1.go_high("+str(t+time)+")")
        for time in switch[ch].time_t1_off:
            exec("coil_ch"+str(ch)+"_1.go_low("+str(t+time)+")")
        for time in switch[ch].time_te_on:
            exec("coil_ch"+str(ch)+"_enable.go_high("+str(t+time)+")")
        # Turning the channels off adds more spikes in the current, read from Hall monitor.

            
    sample_rate=1/(transport_step_size*ms)
    def transport_currents(t, duration, I_channels_interp): # customramp requires the function to be in this specific format.
        return I_channels_interp(t)
    for ch in range(tot_ch):
        exec("coil_ch"+str(ch)+".customramp(t, transport_duration, transport_currents, I_channels_interp["+str(ch)+"], samplerate=sample_rate, units='A')") 
   
    return t + transport_duration
      
def probe_transport_in_progess(t, ind_probe_coils, I_coils):
    probe_coil_duration = 0.5*ms
    transport_time_list = np.arange(0, transport_duration, transport_step_size*ms)
    t_coil_probe = transport.t_coils[ind_probe_coils]-2*ms
    if t_coil_probe<=transport_duration:
        ind_t_coil_probe_start = round(t_coil_probe/transport_duration*len(transport_time_list))
        ind_t_coil_probe_end = min( round((t_coil_probe+probe_coil_duration)/transport_duration*len(transport_time_list)), round((t+transport_duration)/transport_duration*len(transport_time_list)))

        curr_coil1 = I_coils[ind_probe_coils, ind_t_coil_probe_start]
        curr_coil2 = I_coils[ind_probe_coils-1, ind_t_coil_probe_start]
        curr_coil3 = I_coils[ind_probe_coils+1, ind_t_coil_probe_start]

        for coil in range(len(I_coils)):
            I_coils[coil, ind_t_coil_probe_start:] = -0.01
        I_coils[ind_probe_coils,ind_t_coil_probe_start:ind_t_coil_probe_end] = curr_coil1
        I_coils[ind_probe_coils-1,ind_t_coil_probe_start:ind_t_coil_probe_end] = curr_coil2
        I_coils[ind_probe_coils+1,ind_t_coil_probe_start:ind_t_coil_probe_end] = curr_coil3

        coil_ch0_enable.go_low(t+t_coil_probe+probe_coil_duration)
        coil_ch1_enable.go_low(t+t_coil_probe+probe_coil_duration)
        coil_ch2_enable.go_low(t+t_coil_probe+probe_coil_duration)
        coil_ch3_enable.go_low(t+t_coil_probe+probe_coil_duration)
        
        from labscriptlib.RbRb.BEC_functions import probe_XZ
        exec("probe_"+probe_direction+"(t+t_coil_probe+probe_coil_duration+TOF*ms, 'atom')")
        exec("probe_"+probe_direction+"(t+t_coil_probe+probe_coil_duration+TOF*ms+0.2, 'probe')")
