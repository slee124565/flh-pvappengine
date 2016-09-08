from django.shortcuts import render
from datetime import datetime, date

from pvi import PVIType, PVIQueryInfo
from pvi.h5 import controller as h5_controller
from pvi.models import RegData
import pvi.delta_pri_h5 as h5
import os
import pvi

import logging
logger = logging.getLogger(__name__)
    
def query_pvi_info(pvi_name,pvi_type=PVIType.Delta_PRI_H5,query_info=PVIQueryInfo.Energy_Today):
    '''
    return a list of [[datetime,valule],...] information for pvi_name
    '''
    if (pvi_name is None) or (pvi_name == ''):
        logger.error('query_pvi_info for all pvi is not implemented yet.')
        return None
    
    if pvi_type == PVIType.Delta_PRI_H5:
        return h5_controller.query_pvi_info(pvi_name,query_info)
    else:
        logger.error('unknow pvi type %s from name %s' % (pvi_type,pvi_name))
            
def clear_expired_records():
    expired_date = date(date.today().year-1,1,1)
    count, _ = RegData.objects.filter(prob_date__lt = expired_date).delete()
    if count > 0:
        logger.info('clear expired records %d' % count)
    else:
        logger.debug('no expired %s records' % str(expired_date))
    
def get_serial_device_list():
    dev_path_list = []
    SERIAL_DEV_PATH = '/dev/serial/by-id'
    if os.path.exists(SERIAL_DEV_PATH):
        for serial_dev in os.listdir(SERIAL_DEV_PATH):
            #logger.debug('serial device: %s' % serial_dev)
            dev_path_list.append(SERIAL_DEV_PATH + '/' + serial_dev)
    return dev_path_list

def save_all_pvi_input_register_value(pvi_config_list):
    '''
    pvi_config_list json data example
    ::
    
        [
            {
                'name': 'H5',
                'type': 'DELTA_PRI_H5', #-> refer to pvi.PVI_TYPE_LIST
                'modbus_id': 2, #-> pvi modbus address
                'serial': {
                           'port': '/dev/ttyUSB0', #-> deprecated
                           'baudrate': 9600,
                           'bytesize': 8,
                           'parity': serial.PARITY_NONE,
                           'stopbits': 1,
                           'timeout': 0.1,
                           }
            },
        ]    
    '''
    dev_serial_list = get_serial_device_list()
    if len(dev_serial_list) <= 0:
        raise Exception('No serial device found!')
    
    dev_serial_id = dev_serial_list[0]
    logger.info('serial id: %s' % dev_serial_id)
    for pvi_config in pvi_config_list:
        pvi_type = pvi_config.get('type')
        if not pvi_type in pvi.PVI_TYPE_LIST:
            raise Exception('Unknown PVI Type %s' % pvi_type)

        pvi_name = pvi_config.get('name')
        modbus_id = pvi_config.get('modbus_id')
        if pvi_type == pvi.PVI_TYPE_DELTA_PRI_H5:
            logger.info('save RedData for pvi name: %s, type: %s, modbus_id: %s' % 
                        (pvi_name,pvi_type,modbus_id))
            inverter = h5.DeltaPRIH5(dev_serial_id,int(modbus_id))
            inverter.serial.baudrate = pvi_config.get('serial').get('baudrate')
            inverter.serial.bytesize = pvi_config.get('serial').get('bytesize') 
            inverter.serial.parity = pvi_config.get('serial').get('parity') 
            inverter.serial.stopbits = pvi_config.get('serial').get('stopbits')   
            inverter.serial.timeout = pvi_config.get('serial').get('timeout')
            inverter.set_register_measurement_index()
            for reg_name in h5.Register_Polling_List:
                reg_addr = h5.INPUT_REGISTER.get(reg_name)[h5.REGISTER_ADDRESS_COL]
                reg_value = inverter.read_input_register_by_name(reg_name)
                reg_data = RegData(modbus_id=modbus_id,
                                    pvi_name=pvi_name,
                                    #date = datetime.datetime.now(),
                                    address = reg_addr,
                                    value = float(reg_value),
                                    )
                reg_data.save()
                logger.info('save reg_data: %s, %s, %s' % (reg_name, reg_addr, reg_value))

            
    