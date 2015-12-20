from pvi.h5 import *
from pvi.models import RegData
from django import utils
#from datetime import datetime

import logging
logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)
#handler = logging.FileHandler('/home/pi/h5_cron_task.log')
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)
#logger.addHandler(handler)

import minimalmodbus
instr = minimalmodbus.Instrument('/dev/ttyUSB0',2)    
instr.serial.baudrate = 9600    
instr.serial.timeout = 0.1
instr.debug=True

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

def modbus_input_register_read(reg_addr):
    try:
        val = instr.read_register(int(reg_addr)-1,functioncode=4)
        return val
    except IOError as e:
        logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))

def get_register_value_by_name(reg_name):
    reg_entry = INPUT_REGISTER.get(reg_name)
    if reg_entry:
        reg_addr = reg_entry[0]
        reg_len = reg_entry[2]
        reg_value = 0
        logger.debug('reading register: ' + reg_name + ',' + str(reg_addr) + ',' + str(reg_len))
        try:
            if reg_len == 1:
                reg_value = int(modbus_input_register_read(reg_addr))
                logger.debug('1st word value: ' + str(reg_value))
            elif reg_len == 2:
                reg_value = int(modbus_input_register_read(reg_addr))
                logger.debug('1st word value: ' + str(reg_value))
                reg_value += (int(modbus_input_register_read(int(reg_addr)+1))*0x10000)
            else:
                raise Exception('register length ' + str(reg_len) + ' not implement!')
        except TypeError as err:
            logger.warning('read register' + reg_name + ' value fail.')
            return None
    else:
        raise Exception('register name ' + reg_name + ' not know!')

    return reg_value

def save_all_pvi_input_register_value():
    read_log = []
    logger.debug('='*20)
    for reg_name in Register_Polling_List:
        reg_data = INPUT_REGISTER.get(reg_name)
        if (reg_data):
            reg_addr = INPUT_REGISTER[reg_name][0]
            try:
                reg_value = get_register_value_by_name(reg_name)
                if reg_value:
                    reg_data = RegData(modbus_id=MODBUS_ID,
                                pvi_name=PVI_NAME,
                                date = utils.timezone.now(),
                                address = reg_addr,
                                value = float(reg_value),
                                )
                    reg_data.save()
                    logger.info('saved,'+reg_name+','+str(reg_value))
                else:
                    logger.info('not save,'+reg_name)
                read_log.append((reg_name,reg_value))
            except Exception as e:
                logger.error('save pvi input register value error.', exc_info=True)
        else:
            logger.error('unknown register name %s in polling list!' % reg_name)
    logger.debug('read log:'+str(read_log))

