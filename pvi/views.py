#from django.shortcuts import render
from django.db.models import Max
from datetime import datetime, date

from pvi import PVIType, PVIQueryInfo
from pvi.models import RegData, EnergyData
import pvi.delta_pri_h5 as h5
import os
import pvi
from time import sleep
from datetime import timedelta, time

import logging
from pvi.delta_pri_h5 import modbus_id
logger = logging.getLogger(__name__)

def pvi_query_info_energy_hourly_list():
    '''
    provide function for query_pvi_info on PVIQueryInfo.Energy_Hourly_List
    '''
    date_since = (datetime.now() + timedelta(hours=-pvi.MAX_QUERY_ENERGY_HOURLY_LIST_LEN)).date()
    queryset = RegData.objects.filter(address=h5.INPUT_REGISTER['Today Wh'][h5.REGISTER_ADDRESS_COL]
                            ).filter(prob_date__gt=date_since
                            ).values( 'prob_date', 'prob_hour'
                            ).annotate(Max('value')
                            ).order_by('-prob_date','-prob_hour')
    logger.debug('sql cmd: %s' % str(queryset.query))
    info = []
    logger.debug('queryset count %d' % queryset.count())
    max_report_len = pvi.MAX_QUERY_ENERGY_HOURLY_LIST_LEN + 1 # last 48 hours
    if queryset.count() < max_report_len:
        max_report_len = queryset.count()
    for entry in queryset[:max_report_len]:
        #logger.debug(entry['prob_date'])
        #logger.debug(entry['prob_hour'])
        t_hour = entry['prob_hour']
        t_time = time(t_hour,0,0)
        #logger.debug(str(t_time))
        info.append([datetime.combine(entry['prob_date'],t_time),entry['value__max']])
    logger.debug('query return:\n%s' % str(info))
    info.sort(key=lambda x: x[0])

    if len(info) > 0:
        info = [[entry[0],entry[1]*10] for entry in info]
    else:
        logger.warning('no energy sample data in database')
        this_hour_time = datetime.combine(datetime.now().date(), time(datetime.now().hour,0,0))
        for i in range(pvi.MAX_QUERY_ENERGY_HOURLY_LIST_LEN):
            info.append([this_hour_time,0])
            this_hour_time -= timedelta(hours=1)
    
    info.reverse()
    dataset = info
    info = [[dataset[i][0],dataset[i][1]-dataset[i+1][1]] 
    for i in range(len(dataset)-2) 
        if dataset[i][0].date() == dataset[i+1][0].date()]
    info.reverse()
    
    #-> insert zero energy value for missing hour
    dataset = []
    if len(info) > 0:
        dataset.append(info[0])
        t_date = info[0][0]
        i = 1
        while i < len(info):
            t_date = t_date + timedelta(hours=+1)
            if t_date < info[i][0]:
                dataset.append([t_date,0])
            else:
                dataset.append(info[i])
                i += 1        
        dataset.sort(key = lambda x: x[0])

    return dataset

def pvi_query_info_energy_daily_list():
    '''
    provide function for query_pvi_info on PVIQueryInfo.Energy_Daily_List
    '''
    date_since = (datetime.now() + timedelta(days=-pvi.MAX_QUERY_ENERGY_DAILY_LIST_LEN)).date()
    queryset = RegData.objects.filter(address=h5.INPUT_REGISTER['Today Wh'][h5.REGISTER_ADDRESS_COL]
                                        ).filter(prob_date__gt=date_since
                                        ).values('prob_date'
                                        ).annotate(Max('value')
                                        ).order_by('-prob_date')
    info = []
    max_report_len = pvi.MAX_QUERY_ENERGY_DAILY_LIST_LEN #days
    if queryset.count() < max_report_len:
        max_report_len = queryset.count()
    for entry in queryset[:max_report_len]:
        info.append([entry['prob_date'],entry['value__max']])
    logger.debug('query return:\n%s' % str(info))
    info.sort(key=lambda x: x[0])
    
    info = [[entry[0],entry[1]*10] for entry in info]
    return info

def query_pvi_info_h5(pvi_name,pvi_info=PVIQueryInfo.Energy_Today):    
    '''
    all pv inverter type should implement this function for all PVIQueryInfo
    '''
    logger.debug('query_pvi_info({pvi_name},{pvi_info})'.format(pvi_name=pvi_name,pvi_info=pvi_info))
    time_since = (datetime.now() + timedelta(minutes=-30)).time()
    #time_since = datetime.combine(datetime.now().date(),time.min)
    time_until = datetime.now().time()
    logger.debug('query time range %s and %s' % (str(time_since),str(time_until)))

    if pvi_info == PVIQueryInfo.Energy_Today:
        queryset = RegData.objects.filter(address=h5.INPUT_REGISTER['Today Wh'][h5.REGISTER_ADDRESS_COL]
                                ).filter(pvi_name=pvi_name
                                ).values('prob_date'
                                ).annotate(Max('value')
                                ).order_by('prob_date')
        total = len(queryset)
        if (total > 0):
            t_date = queryset[total-1]['prob_date']
            if t_date == datetime.now().date():
                value = queryset[total-1].get('value__max') 
                logger.debug('return %d' % (value * 10))
                return (value * 10)
        else:
            logger.error('empty query result returned')
            return 0
    elif pvi_info == PVIQueryInfo.Energy_This_Month:
        last_month_end_date = date(datetime.now().year,datetime.now().month,1) + timedelta(days=-1)
        queryset = RegData.objects.filter(address=h5.INPUT_REGISTER['Today Wh'][h5.REGISTER_ADDRESS_COL]
                                ).filter(pvi_name=pvi_name
                                ).filter(prob_date__gt=last_month_end_date
                                ).values('prob_date'
                                ).annotate(Max('value')
                                ).order_by('prob_date')
        value = 0
        if len(queryset) > 0:
            for entry in queryset:
                value += entry.get('value__max')
            logger.debug('return %d' % (value * 10))
            return (value * 10)        
        else:
            logger.error('empty query result returned')
            return 0
    elif pvi_info == PVIQueryInfo.Energy_Until_Now:
        queryset = RegData.objects.filter(address=h5.INPUT_REGISTER['DC Life Wh'][h5.REGISTER_ADDRESS_COL]
                                ).filter(pvi_name=pvi_name
                                ).order_by('-date')
        if len(queryset) > 0:
            value = queryset[0].value * 10
            logger.debug('return %d' % (value))
            return (value)
        else:
            logger.error('empty query result returned')
            return 0
    elif pvi_info == PVIQueryInfo.Energy_Hourly_List:
        return pvi_query_info_energy_hourly_list()
    
    elif pvi_info == PVIQueryInfo.Energy_Daily_List:
        return pvi_query_info_energy_daily_list()
    
    elif pvi_info == PVIQueryInfo.AC_Output_Voltage:
        queryset = RegData.objects.filter(address=h5.INPUT_REGISTER['Voltage'][h5.REGISTER_ADDRESS_COL]
                                ).filter(pvi_name=pvi_name
                                ).filter(prob_date__exact=datetime.now().date()
                                ).filter(prob_time__range=[time_since,time_until]
                                ).order_by('-date')
        if len(queryset) > 0:
            value = round(queryset[0].value * 0.1,1)
            logger.debug('return %d' % (value))
            return (value)
        else:
            logger.error('empty query result returned')
    elif pvi_info == PVIQueryInfo.AC_Output_Current:
        queryset = RegData.objects.filter(address=h5.INPUT_REGISTER['Current'][h5.REGISTER_ADDRESS_COL]
                                ).filter(pvi_name=pvi_name
                                ).filter(prob_date__exact=datetime.now().date()
                                ).filter(prob_time__range=[time_since,time_until]
                                ).order_by('-date')
        if len(queryset) > 0:
            value = round(queryset[0].value * 0.01,2)
            logger.debug('return %d' % (value))
            return (value)
        else:
            logger.error('empty query result returned')
    elif pvi_info == PVIQueryInfo.AC_Output_Wattage:
        queryset = RegData.objects.filter(address=h5.INPUT_REGISTER['Wattage'][h5.REGISTER_ADDRESS_COL]
                                ).filter(pvi_name=pvi_name
                                ).filter(prob_date__exact=datetime.now().date()
                                ).filter(prob_time__range=[time_since,time_until]
                                ).order_by('-date')
        if len(queryset) > 0:
            value = queryset[0].value
            logger.debug('return %d' % (value))
            return (value)
        else:
            logger.error('empty query result returned')
    else:
        logger.error('unknow query pvi_info %s' % pvi_info)

def query_pvi_info(pvi_name,pvi_type=PVIType.Delta_PRI_H5,query_info=PVIQueryInfo.Energy_Today):
    '''
    return a list of [[datetime,valule],...] information for pvi_name
    '''
    if (pvi_name is None) or (pvi_name == ''):
        logger.error('query_pvi_info for all pvi is not implemented yet.')
        return None
    
    if pvi_type == PVIType.Delta_PRI_H5:
        return query_pvi_info_h5(pvi_name,query_info)
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
            #inverter.debug = True
            retry_count = 0
            reg_read_success = False
            MAX_RETRY_TIME = 5
            while ( (retry_count < MAX_RETRY_TIME) and (reg_read_success == False) ):
                try:
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
                    reg_read_success = True
                    
                except:
                    retry_count += 1
                    logger.warning('inverter connect exception, try %s!' % retry_count
                                   , exc_info = True)
                    sleep(1)
                    
        logger.info('='*20)
    
def do_action_on_pvs(pvi_config_list, action):
    
    dev_serial_list = get_serial_device_list()
    if len(dev_serial_list) <= 0:
        raise Exception('No serial device found!')
    
    dev_serial_id = dev_serial_list[0]

    for pvi_config in pvi_config_list:
        action(dev_serial_id, pvi_config)

def action_load_pvi_eng_history(dev_serial_id, pvi_config):
    pvi_type = pvi_config.get('type')
    if not pvi_type in pvi.PVI_TYPE_LIST:
        raise Exception('Unknown PVI Type %s' % pvi_type)

#     pvi_name = pvi_config.get('name')
    modbus_id = pvi_config.get('modbus_id')
    if pvi_type == pvi.PVI_TYPE_DELTA_PRI_H5:
        inverter = h5.DeltaPRIH5(dev_serial_id,int(modbus_id))
        inverter.serial.baudrate = pvi_config.get('serial').get('baudrate')
        inverter.serial.bytesize = pvi_config.get('serial').get('bytesize') 
        inverter.serial.parity = pvi_config.get('serial').get('parity') 
        inverter.serial.stopbits = pvi_config.get('serial').get('stopbits')   
        inverter.serial.timeout = pvi_config.get('serial').get('timeout')
        delta_h5_action_with_retry(inverter,delta_h5_load_history)

def delta_h5_action_with_retry(inverter, pvi_action):    
    
    retry_count = 0
    reg_read_success = False
    MAX_RETRY_TIME = 5
    while ( (retry_count < MAX_RETRY_TIME) and (reg_read_success == False) ):
        try:
            reg_read_success = True
            pvi_action(inverter)
        except:
            retry_count += 1
            logger.warning('inverter connect exception, try %s!' % retry_count
                           , exc_info = True)
            sleep(1)

def delta_h5_load_history(inverter):  

    inverter.set_register_measurement_index()
    eng_type_list = ('DAILY', 'MONTHLY')
    
    for eng_type in eng_type_list:
        if eng_type == 'DAILY':
            x_list = inverter.get_energy_day_x_list()
        elif eng_type == 'MONTHLY':
            x_list = inverter.get_energy_month_x_list()
        else:
            raise Exception('eng_type unknown!')
            
        for t_date, t_value in x_list:
            logger.debug('%s,%s' % (t_date,t_value))
            eng_data = EnergyData.objects.get_or_create(
                                modbus_id = inverter.slaveaddress,
                                date = t_date,
                                type = eng_type)
            eng_data.value = t_value
            eng_data.save()
        