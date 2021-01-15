from labscript import *
from labscriptlib.common.utils import Limits
from labscriptlib.common.functions import *
from labscript_utils import import_or_reload
from labscriptlib.RbRb.BEC_functions import *

import_or_reload('labscriptlib.RbRb.mother_connection_table')

MHz = 1e6
us = 1e-6
ms = 1e-3

probe_yz_time = 0.008*ms
probe_xy_time = 0.008*ms
probe_science_time = 0.008*ms


B_bias_optpump = np.array([B_bias_optpump_x,B_bias_optpump_y,B_bias_optpump_z])
B_bias_capture_quad = np.array([B_bias_capture_quad_x,B_bias_capture_quad_y,B_bias_capture_quad_z])
B_bias_final_quad = np.array([B_bias_final_quad_x,B_bias_final_quad_y,B_bias_final_quad_z])
B_bias_tran = 0*np.array([B_bias_tran_x,B_bias_tran_y,B_bias_tran_z])
B_bias_com = np.array([B_bias_com_x,B_bias_com_y, B_bias_com_z])
B_bias_move = 0*np.array([B_bias_mov_x, B_bias_mov_y, B_bias_mov_z])
dur_magtrap = hold_time_start + hold_time_com + dur_quad_ramp


start()
t = 0
Initial_State(t)#82.231 1->1' 84.688 1->2'

t += 0.1

t = MOT_load(t, MOT_load_time, np.array([MOT_B_bias_x,MOT_B_bias_y, MOT_B_bias_z]), MOT_quad_curr, UV_onoff=True)

t = MOT_deload(t)

t += TOF

t = Fluo_image(t, Fluo_image_duration, 'fluo_img')

t += 0.5

t = Fluo_image(t, Fluo_image_duration, 'bg')


Initial_State(t)

t += 1
stop(t)
    