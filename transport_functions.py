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
    I_coils = transport.currents_at_time(transport_time_list) # Only need the time list as imput. The sequence is pre-programmed.

    if inverse:
        I_coils = np.array([np.flip(I_coil) for I_coil in I_coils])
    
    I_channels = np.zeros((tot_ch,len(transport_time_list)))
    curr_ratio=[curr_ratio_ch1, curr_ratio_ch2, curr_ratio_ch3, curr_ratio_ch4]
    
    for ch in range(tot_ch):
        I_channels[ch,:] = transport.currents_for_channel(transport_time_list, transport_duration, ch+1, ratio=curr_ratio[ch], I_coils=I_coils) 
    I_channels_interp = [interp1d(transport_time_list, I_channels[ch,:], 'cubic', fill_value='extrapolate') for ch in range(tot_ch)]
    
    '''
    coil_order_in_I_coils = ['push_coil', 'MOT_quad', 'outer_coil_1', 'inner_coil_1', 'outer_coil_2', 'inner_coil_2', 
                            'outer_coil_3', 'inner_coil_3', 'outer_coil_4', 'inner_coil_4', 'outer_coil_5', 'science_quad']
    '''
    channel_order_in_I_coils = [4, 0, 1, 2, 3, 0, 
                                1, 2, 3, 0, 2, 3]
    ch0_order_in_I_coils = ['', '0', '0', '0', '0', '1', 
                                '1', '1', '1', '0', '0', '0']
    ch1_order_in_I_coils = ['', '0', '0', '0', '0', '0', 
                                '0', '0', '0', '1', '1', '1']
                                
    switch = [current_switch([],[],[],[],[],[]) for ch in range(tot_ch)]
    for coil in range(1,len(I_coils)):
        # Assuming:
            # 1. No negative current
            # 2. Each coil only turns on once
        coil_in_use_time_list = transport_time_list[np.argwhere(I_coils[coil]>0)] 
        if len(coil_dur)>0:
            start, end = coil_in_use_time_list[0][0], coil_in_use_time_list[-1][0]
            switch[channel_order_in_I_coils[coil]].time_te_on.append(start)
            switch[channel_order_in_I_coils[coil]].time_te_off.append(end) # This channel enable off list is never used.
            if ch0_order_in_I_coils[coil]=='0':
                switch[channel_order_in_I_coils[coil]].time_t0_off.append(st)
            elif ch0_order_in_I_coils[coil]=='1':
                switch[channel_order_in_I_coils[coil]].time_t0_on.append(st)
            if ch1_order_in_I_coils[coil]=='0':
                switch[channel_order_in_I_coils[coil]].time_t1_off.append(st)
            elif ch1_order_in_I_coils[coil]=='1':
                switch[channel_order_in_I_coils[coil]].time_t1_on.append(st)
    
    for ch in range(tot_ch):
        for time in switch[ch].time_t0_on:
            exec("ch"+str(ch+1)+"_0.go_high("+str(t+time)+")")
        for time in switch[ch].time_t0_off:
            exec("ch"+str(ch+1)+"_0.go_low("+str(t+time)+")")
        for time in switch[ch].time_t1_on:
            exec("ch"+str(ch+1)+"_1.go_high("+str(t+time)+")")
        for time in switch[ch].time_t1_off:
            exec("ch"+str(ch+1)+"_1.go_low("+str(t+time)+")")
        for time in switch[ch].time_te_on:
            exec("coil_ch"+str(ch+1)+"_enable.go_high("+str(t+time)+")")

    # def Channel_n(n):
        # """
        # n: coild index
        # This function returns the channel indices
        # """
        # if n==0:
            # return 4 # push coil: bias x, bias y
        # if n in [1,5,9]:
            # return 0
        # if n in [2,6]:
            # return 1
        # if n in [3,7,10]:
            # return 2
        # if n in [4,8,11]:
            # return 3
        # if n in [12]:
            # return 1
          
    # #               push    MOT   inner_coil_0        ...                                       science
    # coil_sw_list = ['',    '00',      '00',           '00','00','10','10','10','10','01','01',    '01']
    # switch = [current_switch([],[],[],[],[],[]) for ch in range(4)]
    # for coil in range(1,len(I_coils)):
        # coil_dur = transport_time_list[np.argwhere(I_coils[coil]>0)]
        # if len(coil_dur)>0:
            # st, end = coil_dur[0][0], coil_dur[-1][0]
            # switch[Channel_n(coil)].time_te_on.append(st)
            # switch[Channel_n(coil)].time_te_off.append(end)
            # coil_sw = coil_sw_list[coil]
            # if coil_sw[0]=='0':
                # switch[Channel_n(coil)].time_t0_off.append(st)
            # elif coil_sw[0]=='1':
                # switch[Channel_n(coil)].time_t0_on.append(st)
            # if coil_sw[1]=='0':
                # switch[Channel_n(coil)].time_t1_off.append(st)
            # elif coil_sw[1]=='1':
                # switch[Channel_n(coil)].time_t1_on.append(st)
    
    # def transport_switch(t, duration, switch):
        # for ch in range(4):
            # for time in switch[ch].time_t0_on:
                # exec("ch"+str(ch+1)+"_0.go_high("+str(t+time)+")")
            # for time in switch[ch].time_t0_off:
                # exec("ch"+str(ch+1)+"_0.go_low("+str(t+time)+")")
            # for time in switch[ch].time_t1_on:
                # exec("ch"+str(ch+1)+"_1.go_high("+str(t+time)+")")
            # for time in switch[ch].time_t1_off:
                # exec("ch"+str(ch+1)+"_1.go_low("+str(t+time)+")")
            # for time in switch[ch].time_te_on:
                # exec("coil_ch"+str(ch+1)+"_enable.go_high("+str(t+time)+")")
    
    # transport_switch(t, transport_duration, switch)
    
    sample_rate=1/(transport_step_size*ms)
    def transport_currents(t, duration, I_channels_interp):
        return I_channels_interp(t)
    coil_ch1.customramp(t, transport_duration, transport_currents, I_channels_interp[0], samplerate=sample_rate, units='A')
    coil_ch2.customramp(t, transport_duration, transport_currents, I_channels_interp[1], samplerate=sample_rate, units='A')
    coil_ch3.customramp(t, transport_duration, transport_currents, I_channels_interp[2], samplerate=sample_rate, units='A')
    coil_ch4.customramp(t, transport_duration, transport_currents, I_channels_interp[3], samplerate=sample_rate, units='A')   
    
    
    return t + transport_duration
        