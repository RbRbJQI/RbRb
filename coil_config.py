from labscript import *
from labscriptlib.common.utils import Limits
from labscriptlib.common.functions import *
from labscript_utils import import_or_reload

MHz = 1e6
us = 1e-6
ms = 1e-3

# From MOT to science cell, coil number increases, e.g., outer_coil_1 is closest to the MOT cell.
#                          00                 10            01           11
# coil group 1 includes:  MOT_quad       inner_coil_2   inner_coil_4
# coil group 2 includes:  outer_coil_1   outer_coil_3
# coil_group 3 includes:  inner_coil_1   inner_coil_3   outer_coil_5
# coil_group 4 includes:  outer_coil_2   outer_coil_4   science_quad

def MOT_quad_select(t):
    ch1_0.go_low(t)
    ch1_1.go_low(t)

def outer_coil_1_select(t):
    ch2_0.go_low(t)
    ch2_1.go_low(t)

def inner_coil_1_select(t):
    ch3_0.go_low(t)
    ch3_1.go_low(t)

def outer_coil_2_select(t):
    ch4_0.go_low(t)
    ch4_1.go_low(t)
    
def inner_coil_2_select(t):
    ch1_0.go_high(t)
    ch1_1.go_low(t)
    
def outer_coil_3_select(t):
    ch2_0.go_high(t)
    ch2_1.go_low(t)

def inner_coil_3_select(t):
    ch3_0.go_high(t)
    ch3_1.go_low(t)
    
def outer_coil_4_select(t):
    ch4_0.go_high(t)
    ch4_1.go_low(t)
    
def inner_coil_4_select(t):
    ch1_0.go_low(t)
    ch1_1.go_high(t)
    
def outer_coil_5_select(t):
    ch3_0.go_low(t)
    ch3_1.go_high(t)
    
def science_quad_select(t):
    ch4_0.go_low(t)
    ch4_1.go_high(t)