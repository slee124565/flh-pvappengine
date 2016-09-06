#!/usr/bin/env python


'''
@author: lee_shiueh

.. moduleauthor:: Lee Shiueh <lee.shiueh@gmail.com>

Driver for the Delta PRI H5 PVI communicated wiht Modbus RTU protocol.

'''

import minimalmodbus
import logging
import sys
logger = logging.getLogger(__name__)

__author__  = "Lee Shiueh"
__email__   = "lee.shiueh@gmail.com"
__license__ = "Apache License, Version 2.0"

INPUT_REGISTER = {
    "Delta 5K:Solar 1 RLeakageAvg": [
        "1163",
        "Delta 5K:Solar 1 RLeakageAvg",
        1
    ],
    "Serial number 4,5": [
        "40977",
        "Serial number 4,5",
        1
    ],
    "RTC_Minute": [
        "1037",
        "RTC_Minute",
        1
    ],
    "Event (index+5)": [
        "1094",
        "Event (index+5)",
        1
    ],
    "Delta 5k: Amb Temp": [
        "1080",
        "Delta 5k: Amb Temp",
        1
    ],
    "RTC_Year": [
        "1033",
        "RTC_Year",
        1
    ],
    "Redundant Voltage": [
        "1062",
        "Redundant Voltage",
        1
    ],
    "Current": [
        "1058",
        "Current",
        1
    ],
    "Delta 5k: BoostHs Temp": [
        "1081",
        "Delta 5k: BoostHs Temp",
        1
    ],
    "AC Life Wh": [
        "53252",
        "AC Life Wh",
        2
    ],
    "Reconnected Time": [
        "1049",
        "Reconnected Time",
        1
    ],
    "Delta5k: InvHs Temp": [
        "1082",
        "Delta5k: InvHs Temp",
        1
    ],
    "Adc Wattage": [
        "1070",
        "Adc Wattage",
        1
    ],
    "Adc Redundant Voltage": [
        "1071",
        "Adc Redundant Voltage",
        1
    ],
    "Inverter ID": [
        "1032",
        "Inverter ID",
        1
    ],
    "Event (index+2)": [
        "1091",
        "Event (index+2)",
        1
    ],
    "Wattage": [
        "1059",
        "Wattage",
        1
    ],
    "Event (index+3)": [
        "1092",
        "Event (index+3)",
        1
    ],
    "Event (index+9)": [
        "1098",
        "Event (index+9)",
        1
    ],
    "Event (index+1)": [
        "1090",
        "Event (index+1)",
        1
    ],
    "Serial number 0,1": [
        "40975",
        "Serial number 0,1",
        1
    ],
    "Frequency": [
        "1060",
        "Frequency",
        1
    ],
    "Delta 5K:Solar 1 RLeakage2": [
        "1161",
        "Delta 5K:Solar 1 RLeakage2",
        1
    ],
    "FW2 Revision": [
        "1042",
        "FW2 Revision",
        1
    ],
    "Redundant Frequency": [
        "1063",
        "Redundant Frequency",
        1
    ],
    "Delta 5k:Max BoostHs Temp": [
        "1153",
        "Delta 5k:Max BoostHs Temp",
        1
    ],
    "Serial number 6,7": [
        "40978",
        "Serial number 6,7",
        1
    ],
    "Delta 5K:Adins_adc": [
        "1164",
        "Delta 5K:Adins_adc",
        1
    ],
    "Voltage": [
        "1057",
        "Voltage",
        1
    ],
    "Percentage": [
        "1061",
        "Percentage",
        1
    ],
    "Delta 5K:Solar 1 RLeakage1": [
        "1160",
        "Delta 5K:Solar 1 RLeakage1",
        1
    ],
    "FW1 Date": [
        "1041",
        "FW1 Date",
        1
    ],
    "Inverter Status": [
        "1048",
        "Inverter Status",
        1
    ],
    "FW4 Date": [
        "1047",
        "FW4 Date",
        1
    ],
    "Event (index+4)": [
        "1093",
        "Event (index+4)",
        1
    ],
    "Serial number 10,11": [
        "40980",
        "Serial number 10,11",
        1
    ],
    "Delta 5K:Solar 1 RLeakage3": [
        "1162",
        "Delta 5K:Solar 1 RLeakage3",
        1
    ],
    "Serial number 8,9": [
        "40979",
        "Serial number 8,9",
        1
    ],
    "DC Life Runtime": [
        "1078",
        "DC Life Runtime",
        2
    ],
    "FW4 Revision": [
        "1046",
        "FW4 Revision",
        1
    ],
    "Event (index+7)": [
        "1096",
        "Event (index+7)",
        1
    ],
    "FW3 Revision": [
        "1044",
        "FW3 Revision",
        1
    ],
    "Event (index+6)": [
        "1095",
        "Event (index+6)",
        1
    ],
    "Delta 5k:Max Amb Temp": [
        "1152",
        "Delta 5k:Max Amb Temp",
        1
    ],
    "DC Life Wh": [
        "1076",
        "DC Life Wh",
        2
    ],
    "RTC_Month": [
        "1034",
        "RTC_Month",
        1
    ],
    "RTC_Day": [
        "1035",
        "RTC_Day",
        1
    ],
    "Adc Current": [
        "1069",
        "Adc Current",
        1
    ],
    "RTC_Hour": [
        "1036",
        "RTC_Hour",
        1
    ],
    "RTC_Second": [
        "1038",
        "RTC_Second",
        1
    ],
    "Event (index+0)": [
        "1089",
        "Event (index+0)",
        1
    ],
    "Measurement Index": [
        "1056",
        "Measurement Index",
        1
    ],
    "Event (index+8)": [
        "1097",
        "Event (index+8)",
        1
    ],
    "FW3 Date": [
        "1045",
        "FW3 Date",
        1
    ],
    "FW2 Date": [
        "1043",
        "FW2 Date",
        1
    ],
    "AC Life Runtime": [
        "53254",
        "AC Life Runtime",
        2
    ],
    "Event Index": [
        "1088",
        "Event Index",
        1
    ],
    "FW1 Revision": [
        "1040",
        "FW1 Revision",
        1
    ],
    "Adc Voltage": [
        "1068",
        "Adc Voltage",
        1
    ],
    "Today Wh": [
        "1072",
        "Today Wh",
        2
    ],
    "Serial number 2,3": [
        "40976",
        "Serial number 2,3",
        1
    ],
    "Delta 5k:Max InvHs Temp": [
        "1154",
        "Delta 5k:Max InvHs Temp",
        1
    ],
    "Today Runtime": [
        "1074",
        "Today Runtime",
        2
    ]
}
'''
Constant `INPUT_REGISTER` directory table. 
Take register name as key and value in `RegCol` format
'''

HOLDING_REGISTER = {
    "Measurement Index": [
        "800",
        "Measurement Index",
        1
    ],
    "Event Index" : [
        "801",
        "Event Index",
        1
    ]
}
'''
Constant `HOLDING_REGISTER` directory table. 
Take register name as key and value in `RegCol` format
'''
REGISTER_ADDRESS_COL    = 0
REGISTER_NAME_COL       = 1
REGISTER_LENGTH_COL     = 2

MEASUREMENT_INDEX_CODE_U_GRID   = 0x00
MEASUREMENT_INDEX_CODE_U_DC1    = 0x30
MEASUREMENT_INDEX_CODE_U_DC2    = 0x31
MEASUREMENT_INDEX_CODE_P_BUS    = 0x40
MEASUREMENT_INDEX_CODE_N_BUS    = 0x41

Register_Polling_List = [
                    'Inverter Status',
                    'Measurement Index',
                    'Voltage',
                    'Current',
                    'Wattage',
                    'Frequency',
                    'Percentage',
                    'Redundant Voltage',
                    'Redundant Frequency',
                    'Adc Voltage',
                    'Adc Current',
                    'Adc Wattage',
                    'Adc Redundant Voltage',
                    'Today Wh',
                    'Today Runtime',
                    'DC Life Wh',
                    'DC Life Runtime',
                    ]

class DeltaPRIH5(minimalmodbus.Instrument):
    '''Instrument class for Delta PRI-H5 PV Inverter.
    
    Communicates via Modbus RTU protocol (via RS232 or RS485), using the *MinimalModbus* Python module.
    
    Args:
        * portname (str): port name
        * slaveaddress (int): slave address in the range 1 to 247
        
    Implemented with these function codes (in decimal):

    ==================  ====================
    Description         Modbus function code
    ==================  ====================
    Read registers      4
    Write registers     6
    ==================  ====================
    
    
    '''


    def __init__(self, portname, slaveaddress):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)


    def read_input_register_by_name(self, reg_name):
        try:
            reg_entry = INPUT_REGISTER.get(reg_name)
            if reg_entry:
                reg_addr = reg_entry[0]
                reg_len = reg_entry[2]
                reg_value = 0
                logger.debug('reading register: ' + reg_name + ',' + str(reg_addr) + ',' + str(reg_len))

                if reg_len == 1:
                    reg_value = int(self.read_register(int(reg_addr)-1,functioncode=4))
                    logger.debug('1st word value: ' + str(reg_value))
                elif reg_len == 2:
                    reg_value = int(self.read_register(int(reg_addr)-1,functioncode=4))
                    logger.debug('1st word value: ' + str(reg_value))
                    reg_value += (int(self.read_register(int(reg_addr),functioncode=4))*0x10000)
                else:
                    raise Exception('register length ' + str(reg_len) + ' not implement!')
            else:
                raise Exception('register name ' + reg_name + ' not know!')

        except IOError as e:
            logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
            return None

        except TypeError:
            logger.warning('read register ' + reg_name + ' value fail.', exc_info=True)
            return None
    
        return reg_value
    
    def set_register_measurement_index(self, value = MEASUREMENT_INDEX_CODE_U_GRID):
        logger.debug('set_register_measurement_index: %s' % value)
        reg_name = 'Measurement Index'
        self.write_register(int(HOLDING_REGISTER[reg_name][REGISTER_ADDRESS_COL])-1, 
                              MEASUREMENT_INDEX_CODE_U_GRID,
                              functioncode = 6)
        
if __name__ == '__main__':
    
    usage = 'Usage: python %s <serial_port> <modbus_id>' % sys.argv[0]
    
    #serial_by_id = '/dev/ttyUSB0'
    #modbus_id = 2
    if len(sys.argv) > 2:
        serial_by_id = sys.argv[1]
        modbus_id = sys.argv[2]
    else:
        minimalmodbus._print_out('Python Script Param Error!')
        minimalmodbus._print_out(usage)
        sys.exit(0) 
    
    minimalmodbus._print_out('Testing Delta PVI PRI-H5 with serial port: %s and modbus ID: %s' % (serial_by_id, modbus_id))

    instr = DeltaPRIH5(serial_by_id,modbus_id)
    instr.serial.baudrate = 9600
    instr.serial.bytesize = 8
    instr.serial.parity = 'N'
    instr.serial.stopbits = 1    
    instr.serial.timeout = 0.1
    #instr.debug=True
    
    minimalmodbus._print_out('set Measurement Index to GRID ...')
    instr.set_register_measurement_index()
    
    for reg_name in Register_Polling_List:
        reg_data = INPUT_REGISTER.get(reg_name)
        reg_addr = INPUT_REGISTER[reg_name][REGISTER_ADDRESS_COL]
        minimalmodbus._print_out('read register value for name: %s, address: %s ...' % (reg_name,reg_addr))
        reg_value = instr.read_input_register_by_name(reg_name)
        minimalmodbus._print_out('%s, %s, %s' % (reg_name, reg_addr, reg_value))
        minimalmodbus._print_out('-'*20)
    
