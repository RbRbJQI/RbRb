from labscript import *
from labscript_utils import h5_lock
from labscript_utils import import_or_reload
from labscript_utils.unitconversions.linear_coil_driver import BidirectionalCoilDriver
from labscript_utils.unitconversions.AOMAMP import AOMAMP
from labscript_utils.unitconversions.quad_driver import quad_driver
from labscript_utils.unitconversions.quad_driver_2 import quad_driver_2

from labscript_devices.NI_DAQmx.labscript_devices import NI_USB_6229
from labscript_devices.NI_DAQmx.labscript_devices import NI_PCIe_6738
from labscript_devices.NI_DAQmx.labscript_devices import NI_DAQmx
from labscript_devices.NI_DAQmx.labscript_devices import NI_USB_6002


'''

DEV 1

'''

NI_USB_6002(name='ni_usb_6002',
         parent_device=ni_usb_6002_clock,
         MAX_name='Dev1',
		 clock_terminal='/Dev1/PFI1')
AnalogIn(name='ai0', parent_device=ni_usb_6002, connection='ai0')
AnalogIn(name='ai1', parent_device=ni_usb_6002, connection='ai1')
AnalogIn(name='ai2', parent_device=ni_usb_6002, connection='ai2')
AnalogIn(name='ai3', parent_device=ni_usb_6002, connection='ai3')



'''

DEV 3

AOM
Shutters

'''

NI_USB_6229(name='ni_usb_6229_table2',
         parent_device=ni_usb_6229_table2_clock,
         MAX_name='Dev3',
         clock_terminal='/Dev3/PFI0')
DigitalOut(name='Repump_AOM', parent_device=ni_usb_6229_table2, connection='port0/line0')
DigitalOut(name='Probe_AOM', parent_device=ni_usb_6229_table2, connection='port0/line1')
DigitalOut(name='Cooling_AOM', parent_device=ni_usb_6229_table2, connection='port0/line2')
DigitalOut(name='do3', parent_device=ni_usb_6229_table2, connection='port0/line3')
DigitalOut(name='OptPump_AOM', parent_device=ni_usb_6229_table2, connection='port0/line4')
DigitalOut(name='evap_switch', parent_device=ni_usb_6229_table2, connection='port0/line5')
DigitalOut(name='do6', parent_device=ni_usb_6229_table2, connection='port0/line6')
DigitalOut(name='do7', parent_device=ni_usb_6229_table2, connection='port0/line7')
DigitalOut(name='do8', parent_device=ni_usb_6229_table2, connection='port0/line8')
DigitalOut(name='do9', parent_device=ni_usb_6229_table2, connection='port0/line9')

Shutter(name='Cooling_shutter', parent_device=ni_usb_6229_table2, connection='port0/line12', delay=(3*ms, 3*ms))
Shutter(name='Repump_shutter', parent_device=ni_usb_6229_table2, connection='port0/line15', delay=(6*ms, 3*ms))
Shutter(name='OptPump_shutter', parent_device=ni_usb_6229_table2, connection='port0/line14', delay=(2.1*ms, 3.3*ms))
Shutter(name='Probe_shutter', parent_device=ni_usb_6229_table2, connection='port0/line13', delay=(3.3*ms, 3*ms))

AnalogOut(name='quad_MOT2', parent_device=ni_usb_6229_table2, connection='ao0')
AnalogOut(name='x_shim', parent_device=ni_usb_6229_table2, connection='ao1', unit_conversion_class=BidirectionalCoilDriver, unit_conversion_parameters={'slope':1.96, 'shift':-0.11*1.96})
AnalogOut(name='y_shim', parent_device=ni_usb_6229_table2, connection='ao2', unit_conversion_class=BidirectionalCoilDriver, unit_conversion_parameters={'slope':1.96, 'shift':0.076*1.96})
AnalogOut(name='z_shim', parent_device=ni_usb_6229_table2, connection='ao3', unit_conversion_class=BidirectionalCoilDriver, unit_conversion_parameters={'slope':1.96, 'shift':0.004*1.96})
AnalogIn(name='Cooling_monitor', parent_device=ni_usb_6229_table2, connection='ai0')
AnalogIn(name='testin_table1', parent_device=ni_usb_6229_table2, connection='ai1')
AnalogIn(name='testin_table4', parent_device=ni_usb_6229_table2, connection='ai2')
AnalogIn(name='testin_table3', parent_device=ni_usb_6229_table2, connection='ai3')
AnalogIn(name='Repump_monitor', parent_device=ni_usb_6229_table2, connection='ai4')
AnalogIn(name='testin_table5', parent_device=ni_usb_6229_table2, connection='ai5')



'''

DEV 4

Lasers

'''

NI_PCIe_6738(name='ni_pcie_6738',  parent_device= NI6738_clock, 
        MAX_name='Dev4', clock_terminal='/Dev4/PFI0', max_AO_sample_rate = 400e3)
AnalogOut(name='Repump_int', parent_device=ni_pcie_6738, connection='ao2', unit_conversion_class=AOMAMP, unit_conversion_parameters={'shift':0.057})
AnalogOut(name='Cooling_int', parent_device=ni_pcie_6738, connection='ao3', unit_conversion_class=AOMAMP, unit_conversion_parameters={'shift':0.058})
AnalogOut(name='Probe_int', parent_device=ni_pcie_6738, connection='ao4', unit_conversion_class=AOMAMP, unit_conversion_parameters={'shift':0.060})
AnalogOut(name='OptPump_int', parent_device=ni_pcie_6738, connection='ao5', unit_conversion_class=AOMAMP, unit_conversion_parameters={'shift':0.060})
AnalogOut(name='evap_int', parent_device=ni_pcie_6738, connection='ao6')
AnalogOut(name='Dipole_Power_tot_int', parent_device=ni_pcie_6738, connection='ao7')
AnalogOut(name='Dipole_Power_1_int', parent_device=ni_pcie_6738, connection='ao8')
AnalogOut(name='Dipole_Power_2_int', parent_device=ni_pcie_6738, connection='ao9')



'''

DEV 5

Transport

'''

NI_USB_6229(name='ni_usb_6229',
         parent_device=ni_usb_6229_clock,
         MAX_name='Dev5',
         clock_terminal='/Dev5/PFI0')
DigitalOut(name='coil_ch1_enable', parent_device=ni_usb_6229, connection='port0/line0')
DigitalOut(name='ch1_0', parent_device=ni_usb_6229, connection='port0/line1')
DigitalOut(name='ch1_1', parent_device=ni_usb_6229, connection='port0/line2')
DigitalOut(name='coil_ch2_enable', parent_device=ni_usb_6229, connection='port0/line3')
DigitalOut(name='ch2_0', parent_device=ni_usb_6229, connection='port0/line4')
DigitalOut(name='ch2_1', parent_device=ni_usb_6229, connection='port0/line5')
DigitalOut(name='coil_ch3_enable', parent_device=ni_usb_6229, connection='port0/line6')
DigitalOut(name='ch3_0', parent_device=ni_usb_6229, connection='port0/line7')
DigitalOut(name='ch3_1', parent_device=ni_usb_6229, connection='port0/line8')
DigitalOut(name='coil_ch4_enable', parent_device=ni_usb_6229, connection='port0/line9')
DigitalOut(name='ch4_0', parent_device=ni_usb_6229, connection='port0/line10')
DigitalOut(name='ch4_1', parent_device=ni_usb_6229, connection='port0/line11')
DigitalOut(name='x_shim_disable', parent_device=ni_usb_6229, connection='port0/line12')
DigitalOut(name='y_shim_disable', parent_device=ni_usb_6229, connection='port0/line13')
DigitalOut(name='z_shim_disable', parent_device=ni_usb_6229, connection='port0/line14')
DigitalOut(name='UV', parent_device=ni_usb_6229, connection='port0/line15')

AnalogOut(name='coil_ch1', parent_device=ni_usb_6229, connection='ao0', unit_conversion_class=quad_driver, unit_conversion_parameters={'A_per_V':-40, 'Gcm_per_A':2.4, 'A_offset':0, 'A_min':0} )
AnalogOut(name='coil_ch2', parent_device=ni_usb_6229, connection='ao1', unit_conversion_class=quad_driver, unit_conversion_parameters={'A_per_V':-12, 'Gcm_per_A':2.4, 'A_offset':0, 'A_min':0})
AnalogOut(name='coil_ch3', parent_device=ni_usb_6229, connection='ao2', unit_conversion_class=quad_driver, unit_conversion_parameters={'A_per_V':-40, 'Gcm_per_A':2.4, 'A_offset':0, 'A_min':0})
AnalogOut(name='coil_ch4', parent_device=ni_usb_6229, connection='ao3', unit_conversion_class=quad_driver, unit_conversion_parameters={'A_per_V':-40, 'Gcm_per_A':2.4, 'A_offset':0, 'A_min':0})
AnalogIn(name='testin0', parent_device=ni_usb_6229, connection='ai0')
AnalogIn(name='testin1', parent_device=ni_usb_6229, connection='ai1')
AnalogIn(name='testin2', parent_device=ni_usb_6229, connection='ai2')
AnalogIn(name='testin3', parent_device=ni_usb_6229, connection='ai3')
AnalogIn(name='testin4', parent_device=ni_usb_6229, connection='ai4')
AnalogIn(name='testin5', parent_device=ni_usb_6229, connection='ai5')
AnalogIn(name='testin6', parent_device=ni_usb_6229, connection='ai6')



