
from pvi.h5 import *
from pvi.models import RegData
from django.db.models import Max

import logging, sys, datetime
logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)
#handler = logging.FileHandler('/home/pi/h5_cron_task.log')
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)
#logger.addHandler(handler)

import minimalmodbus
if not sys.platform == 'win32':
    instr = minimalmodbus.Instrument('/dev/ttyUSB0',2)    
    instr.serial.baudrate = 9600    
    instr.serial.timeout = 0.1
    instr.debug=True

import time

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
            logger.warning('read register ' + reg_name + ' value fail.')
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
                count = 1
                while (reg_value is None) and (count < 3):
                    logger.warning('read [' + reg_name + '] fail, retry ' + str(count) + ' after 5 seconds.')
                    time.sleep(5)
                    reg_value = get_register_value_by_name(reg_name)
                    count += 1
                    
                if not reg_value is None:
                    reg_data = RegData(modbus_id=MODBUS_ID,
                                pvi_name=PVI_NAME,
                                #date = datetime.datetime.now(),
                                address = reg_addr,
                                value = float(reg_value),
                                )
                    reg_data.save()
                    logger.debug('saved,'+reg_name+','+str(reg_value))
                else:
                    logger.debug('not save,'+reg_name)
                read_log.append((reg_name,reg_value))
            except Exception as e:
                logger.error('save pvi input register value error.', exc_info=True)
        else:
            logger.error('unknown register name %s in polling list!' % reg_name)
    logger.info('dump: '+str(read_log))

def get_pvi_energy_info_json(period_type='daily'):
    register_name = 'Today Wh'
    register_address = INPUT_REGISTER.get(register_name)[RegCol.address.value]
    logger.debug('get_pvi_energy_info_json with period_type %s' % period_type)
    if period_type == 'hourly':
        queryset = RegData.objects.filter(address=register_address
                                ).values( 'prob_date', 'prob_hour'
                                ).annotate(Max('value')
                                ).order_by('-prob_date','-prob_hour')
        logger.debug('sql cmd: %s' % str(queryset.query))
        info = []
        logger.debug('queryset count %d' % queryset.count())
        max_report_len = 48 # last 48 hours
        if queryset.count() < max_report_len:
            max_report_len = queryset.count()
        for entry in queryset[:max_report_len]:
            #logger.debug(entry['prob_date'])
            #logger.debug(entry['prob_hour'])
            t_hour = entry['prob_hour']
            t_time = datetime.time(t_hour,0,0)
            #logger.debug(str(t_time))
            info.append([datetime.datetime.combine(entry['prob_date'],t_time),entry['value__max']])
        logger.debug('query return:\n%s' % str(info))
    elif period_type == 'daily':
        queryset = queryset = RegData.objects.filter(address=register_address
                                            ).values('prob_date'
                                            ).annotate(Max('value')
                                            ).order_by('-prob_date')
        info = []
        max_report_len = 45 #days
        if queryset.count() < max_report_len:
            max_report_len = queryset.count()
        for entry in queryset[:max_report_len]:
            info.append([entry['prob_date'],entry['value__max']])
        logger.debug('query return:\n%s' % str(info))
        info.sort(key=lambda x: x[0])
        
    else:
        return None
    
    #-> each unit read is 10Wh
    info = [[entry[0],entry[1]*10] for entry in info]
    return info


if __name__ == '__main__':
    while True:
        save_all_pvi_input_register_value()
        time.sleep(5)
