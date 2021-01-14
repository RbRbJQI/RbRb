from labscript import *
from labscriptlib.common.utils import Limits
from labscriptlib.common.functions import *
from labscript_utils import import_or_reload
from labscriptlib.RbRb.BEC_functions import *

import_or_reload('labscriptlib.RbRb.connection_table')
MHz = 1e6
us = 1e-6
ms = 1e-3
nt_step = 0.15*ms
#calibrated intensity zeros
probe_z = -0.06
cool_z = -0.058
rep_z = -0.057
opt_z = -0.06
#
import_or_reload('labscriptlib.RbRb.transport.new_transport_optimisation')
from labscriptlib.RbRb.transport.new_transport_optimisation import transport
tswitch = transport.t_switchover

probe_yz_time = 0.008*ms
probe_xy_time = 0.008*ms
probe_science_time = 0.008*ms
probe_fluo_time = 1*ms

B_bias_mol = (0,0,B_bias_mol_z)#*np.array([B_bias_mol_x,B_bias_mol_y,B_bias_mol_z])
B_bias_optpump = np.array([B_bias_optpump_x,B_bias_optpump_y,B_bias_optpump_z])
B_bias_capture_quad = np.array([B_bias_capture_quad_x,B_bias_capture_quad_y,B_bias_capture_quad_z])
B_bias_final_quad = np.array([B_bias_final_quad_x,B_bias_final_quad_y,B_bias_final_quad_z])
B_bias_tran = 0*np.array([B_bias_tran_x,B_bias_tran_y,B_bias_tran_z])
B_bias_com = np.array([B_bias_com_x,B_bias_com_y, B_bias_com_z])
B_bias_MOT = np.array([B_bias_mot_x,B_bias_mot_y, B_bias_mot_z])
B_bias_move = 0*np.array([B_bias_mov_x, B_bias_mov_y, B_bias_mov_z])
dur_magtrap = hold_time_start + hold_time_com + dur_quad_ramp
start()
t = 0

New_MOT = MOT(t, cooling_freq=cent, repump_freq=repump_freq, quad_curr=quad) #82.231 1->1' 84.688 1->2'
t += 1e-3
# exec("New_MOT.probe_"+probe_direction+"(t, probe_"+probe_direction+"_time, 'bg')")#exec for abs imaging
t += 30e-3
# t += New_MOT.probe_fluo(t, probe_fluo_time, 'bg') # fluo imaging
t += 30e-3
# New_MOT.probe_science(t, probe_yz_time, 'bg') 
# New_MOT.probe_science(t, sci_probe_time, 'bg') #science cell abs imaging
t+= 30e-3


t = New_MOT.load(t, load_time, B_bias_MOT, UV_onoff=True)
# MOT_YZ_flea.expose(t-10*ms,'MOT_fluo_img', trigger_duration=0.1*ms, frametype='fluo_img')
# t = New_MOT.move(t, dur_MOT_move, np.array(B_bias_MOT), np.array(B_bias_move))
#t = New_MOT.compress(t, CMOT_dur, quad, compressed_MOT_quad, res+compress_freq_start*MHz, res+compress_freq_end*MHz, np.array(B_bias_move), np.array(B_bias_com)) # CMOT


#t = New_MOT.pol_grad(t, dur_mol, molasses_freq_start, molasses_freq_end, np.array(B_bias_mol)) # Molasses
# # t = New_MOT.depump(t,4*ms) 
#t=New_MOT.opt_pump(t, duration=dur_OptPumping*ms)
#t = New_MOT.mag_trap(t, duration=dur_magtrap*ms, quad_start=quad_trap, B_bias_start=np.array(B_bias_capture_quad), B_bias_final= np.array(B_bias_final_quad))


# # t = New_MOT.move(t, dur_tran_bias*ms, np.array(B_bias_final_quad), np.array(B_bias_tran))

# t = New_MOT.new_transport(t, duration= dur_transport, B_bias_start=np.array(B_bias_tran), bias_r_yx=bias_ratio_yx)
# t = New_MOT.new_transport(t, duration= dur_transport, B_bias_start=np.array(B_bias_tran), bias_r_yx=bias_ratio_yx, inverse=True)
# t = New_MOT.evap(t, dur_evap)

New_MOT.deload(t)
t += t_of_f
New_MOT.probe_fluo(t, probe_fluo_time, 'fluo_img')
# New_MOT.probe_science(t, sci_probe_time, 'atom')
# exec("New_MOT.probe_"+str(probe_direction)+"(t, probe_"+probe_direction+"_time, 'atom')")
t += 0.2
# New_MOT.probe_science(t, sci_probe_time, 'probe')
# exec("New_MOT.probe_"+str(probe_direction)+"(t, probe_"+probe_direction+"_time, 'probe')")



t+=0.3
t = New_MOT.probe_fluo(t, probe_fluo_time, 'bg')
# New_MOT.fluorescence(0,t)

New_MOT.__init__(t, cooling_freq=cent, repump_freq=repump_freq, quad_curr=quad)
# UV.go_high(t)

# set_freq(Cooling, t-0.01, cent)
# New_MOT.set_bias(t-0.01, [0,0,0])
# quad_MOT.constant(t-0.01,value=1)
# # transport1.constant(t-0.01,value=1)
# # Cool_int.constant(t+0.12*ms, 0)
# # Repump_int.constant(t+0.12*ms, 0)
# Shutter_Probe.close(t)
# # t+=9
# # plt.show()
t+=1
stop(t)
    