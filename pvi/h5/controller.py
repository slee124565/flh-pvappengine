
from pvi.h5 import *
import pvi
from pvi.models import RegData
from django.db.models import Max
from datetime import datetime, date, time, timedelta
from pvi import *
from dbconfig.views import get_app_json_db_config

import logging, sys
logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)
#handler = logging.FileHandler('/home/pi/h5_cron_task.log')
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)
#logger.addHandler(handler)

t_pvs_config = get_app_json_db_config('pvi',pvi.DEFAULT_DB_CONFIG)[0]
t_serial_port = t_pvs_config['serial']['port']
t_modbus_id = t_pvs_config['modbus_id']
t_pvs_name = t_pvs_config['name']
t_pvs_type = t_pvs_config['type']
logger.info('pvs[0] meta: {pvs_meta}'.format(pvs_meta=str(t_pvs_config)))

import minimalmodbus, os
if os.path.exists(t_serial_port):
    instr = minimalmodbus.Instrument(t_serial_port,t_modbus_id)    
    instr.serial.baudrate = t_pvs_config['serial']['baudrate']
    instr.serial.bytesize = t_pvs_config['serial']['bytesize']
    instr.serial.parity = t_pvs_config['serial']['parity']
    instr.serial.stopbits = t_pvs_config['serial']['stopbits']    
    instr.serial.timeout = t_pvs_config['serial']['timeout']
    instr.debug=True
else:
    logger.warning('pvi connection is not exist! enter simulation mode')


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
    '''
    read Input Register value (2 bytes)
    '''
    try:
        val = instr.read_register(int(reg_addr)-1,functioncode=4)
        return val
    except IOError as e:
        logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))

def get_register_value_by_name(reg_name):
    '''
    read Input Register value according to it length (2 or 4 bytes) with word order
    '''
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
            logger.warning('read register ' + reg_name + ' value fail.', exc_info=True)
            return None
    else:
        raise Exception('register name ' + reg_name + ' not know!')

    return reg_value

def check_n_set_measurement_index():
    """check PRI H5 inverter `Measurement Index` register value
    and set to U grid(0x00) if register value has been changed."""
    reg_name = 'Measurement Index'
    reg_value = get_register_value_by_name(reg_name)
    if reg_value != MeasurementIndexCodeEnum.u_grid.value:
        logger.warning('inverter Measurement Index value %d is not U Grid config value %d, reset it' %(reg_value,
                                                            MeasurementIndexCodeEnum.u_grid.value))
        instr.write_register(int(HOLDING_REGISTER[reg_name][RegCol.address.value])-1, 
                              MeasurementIndexCodeEnum.u_grid.value,
                              functioncode = 6)
        if get_register_value_by_name(reg_name) != MeasurementIndexCodeEnum.u_grid.value:
            logger.error('reset Measurement Index register failed')
    else:
        logger.debug('inverter Measurement Index value check passed')

def save_all_pvi_input_register_value():
    '''
    save all Input Register in Register_Polling_List into database
    '''
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
                    reg_data = RegData(modbus_id=t_modbus_id,
                                pvi_name=t_pvs_name,
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
    '''
    return pvi daily or hourly energy information in json format
    '''
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
            t_time = time(t_hour,0,0)
            #logger.debug(str(t_time))
            info.append([datetime.combine(entry['prob_date'],t_time),entry['value__max']])
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

def get_polling_input_register_value():
    '''
    return a list [(reg_name,reg_value)...] of Register_Polling_List
    '''
    info = []
    for reg_name in Register_Polling_List:
        reg_value = get_register_value_by_name(reg_name)
        info.append([reg_name,reg_value])
    return info

def pvi_query_info_energy_hourly_list():
    '''
    provide function for query_pvi_info on PVIQueryInfo.Energy_Hourly_List
    '''
    queryset = RegData.objects.filter(address=INPUT_REGISTER['Today Wh'][RegCol.address.value]
                            ).values( 'prob_date', 'prob_hour'
                            ).annotate(Max('value')
                            ).order_by('-prob_date','-prob_hour')
    logger.debug('sql cmd: %s' % str(queryset.query))
    info = []
    logger.debug('queryset count %d' % queryset.count())
    max_report_len = MAX_QUERY_ENERGY_HOURLY_LIST_LEN + 1 # last 48 hours
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
        for i in range(MAX_QUERY_ENERGY_HOURLY_LIST_LEN):
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
    queryset = RegData.objects.filter(address=INPUT_REGISTER['Today Wh'][RegCol.address.value]
                                        ).values('prob_date'
                                        ).annotate(Max('value')
                                        ).order_by('-prob_date')
    info = []
    max_report_len = MAX_QUERY_ENERGY_DAILY_LIST_LEN #days
    if queryset.count() < max_report_len:
        max_report_len = queryset.count()
    for entry in queryset[:max_report_len]:
        info.append([entry['prob_date'],entry['value__max']])
    logger.debug('query return:\n%s' % str(info))
    info.sort(key=lambda x: x[0])
    
    info = [[entry[0],entry[1]*10] for entry in info]
    return info
        
def query_pvi_info(pvi_name,pvi_info=PVIQueryInfo.Energy_Today):
    '''
    all pv inverter type should implement this function for all PVIQueryInfo
    '''
    logger.debug('query_pvi_info({pvi_name},{pvi_info})'.format(pvi_name=pvi_name,pvi_info=pvi_info))
    time_since = (datetime.now() + timedelta(minutes=-30)).time()
    #time_since = datetime.combine(datetime.now().date(),time.min)
    time_until = datetime.now().time()
    logger.debug('query time range %s and %s' % (str(time_since),str(time_until)))

    if pvi_info == PVIQueryInfo.Energy_Today:
        queryset = RegData.objects.filter(address=INPUT_REGISTER['Today Wh'][RegCol.address.value]
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
        queryset = RegData.objects.filter(address=INPUT_REGISTER['Today Wh'][RegCol.address.value]
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
        queryset = RegData.objects.filter(address=INPUT_REGISTER['DC Life Wh'][RegCol.address.value]
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
        queryset = RegData.objects.filter(address=INPUT_REGISTER['Voltage'][RegCol.address.value]
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
        queryset = RegData.objects.filter(address=INPUT_REGISTER['Current'][RegCol.address.value]
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
        queryset = RegData.objects.filter(address=INPUT_REGISTER['Wattage'][RegCol.address.value]
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

if __name__ == '__main__':
    while True:
        save_all_pvi_input_register_value()
        time.sleep(5)
