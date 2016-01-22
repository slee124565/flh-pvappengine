from django.http import HttpResponse
from django.conf import settings
from enum import Enum

from pvappengine import *
from pvi.views import query_pvi_info
from pvi import *
import accuweather.views as accuweather_api
from accuweather import CurrConditionType

import logging, json
logger = logging.getLogger(__name__)

kWh_carbon_save_unit_kg = settings.PVS_CONFIG['kWh_carbon_save_unit_kg']
kWh_income_unit_ntd = settings.PVS_CONFIG['kWh_income_unit_ntd']


pvs_meta = {
            'pvs_static': {
                           'today': {
                                     'total_eng_kwh':0,
                                     'total_carbon_save':0,
                                     'total_income':0,
                                     },
                           'this_month': {
                                     'total_eng_kwh':0,
                                     'total_carbon_save':0,
                                     'total_income':0,
                                     },
                           'until_now': {
                                     'total_eng_kwh':0,
                                     'total_carbon_save':0,
                                     'total_income':0,
                                     },
                           },
            'dc_output': {
                          },
            'environment': {
                            'uv_index':0,
                            'temperature':0,
                            'visibility':0,
                            },
            }

def get_pvi_list_from_settings():
    '''
    return list of pvi name according to settings module's PVS_CONFIG
    '''
    return [entry['name'] for entry in settings.PVS_CONFIG['pvs']]

def get_pvi_type(pvi_name):
    '''
    string mapping for element in PVI_TYPE_LIST to PVIType
    '''
    for entry in settings.PVS_CONFIG['pvs']:
        if entry['name'] == pvi_name:
            if entry['type'] == PVI_TYPE_DELTA_PRI_H5:
                return PVIType.Delta_PRI_H5
    
def add_pvi_info_into_pvs_meta(pvi_name, pvi_type):
    '''
    return all pvi information according to pvs_meta template
    '''
    t_value = query_pvi_info(pvi_name, pvi_type, PVIQueryInfo.Energy_Today)
    if not t_value is None:
        pvs_meta['pvs_static']['today']['total_eng_kwh'] += round(0.001 * t_value, 3)
    
    t_value = query_pvi_info(pvi_name, pvi_type, PVIQueryInfo.Energy_This_Month)
    if not t_value is None:
        pvs_meta['pvs_static']['this_month']['total_eng_kwh'] += round(0.001 * t_value, 3)

    t_value = query_pvi_info(pvi_name, pvi_type, PVIQueryInfo.Energy_Until_Now)
    if not t_value is None:
        pvs_meta['pvs_static']['until_now']['total_eng_kwh'] += round(0.001 * t_value, 3)
    
    if not pvi_name in pvs_meta['dc_output'].keys():
        pvs_meta['dc_output'][pvi_name] = {
                                           'voltage': 'N/A',
                                           'current': 'N/A',
                                           'wattage': 'N/A',
                                           }
    voltage = query_pvi_info(pvi_name, pvi_type, PVIQueryInfo.AC_Output_Voltage)
    if not (voltage is None):
        pvs_meta['dc_output'][pvi_name]['voltage'] = round(voltage,1)

    current = query_pvi_info(pvi_name, pvi_type, PVIQueryInfo.AC_Output_Current)
    if not (current is None):
        pvs_meta['dc_output'][pvi_name]['current'] = round(current,2)

    wattage = query_pvi_info(pvi_name, pvi_type, PVIQueryInfo.AC_Output_Wattage)
    if not (wattage is None):
        pvs_meta['dc_output'][pvi_name]['wattage'] = wattage

def add_environment_condition_into_pvs_meta():
    '''
    add environment's uv_index, temperature and visibility into pvs_meta template
    '''
    env_conditions = accuweather_api.get_current_conditions()
    pvs_meta['environment']['uv_index'] = env_conditions[CurrConditionType.UV_Index]
    pvs_meta['environment']['temperature'] = env_conditions[CurrConditionType.Temperature]
    pvs_meta['environment']['visibility'] = env_conditions[CurrConditionType.Visibility]

def query_pvs_meta(request,pvi_name=None):
    '''
    Web Application API
    provide PVStation page need information json data
    '''
    pvs_meta['pvs_static']['today']['total_eng_kwh'] = 0
    pvs_meta['pvs_static']['this_month']['total_eng_kwh'] = 0
    pvs_meta['pvs_static']['until_now']['total_eng_kwh'] = 0
    
    pvi_list = get_pvi_list_from_settings()
    if pvi_name is None:
        # TODO: need to verify for multiple pvi pvstation
        logger.info('query_pvs_meta for all pvi')
        for name in pvi_list:
            pvi_type = get_pvi_type(name)
            add_pvi_info_into_pvs_meta(name,pvi_type)
    else:
        logger.info('query_pvs_meta for pvi %s' % pvi_name)
        pvi_type = get_pvi_type(pvi_name)
        add_pvi_info_into_pvs_meta(pvi_name,pvi_type)
        
    add_environment_condition_into_pvs_meta()
    pvs_meta['pvs_static']['today']['total_carbon_save'] = '{:,.2f}'.format(kWh_carbon_save_unit_kg 
                                                    * pvs_meta['pvs_static']['today']['total_eng_kwh'])
    pvs_meta['pvs_static']['today']['total_income'] = '{:,.2f}'.format(kWh_income_unit_ntd 
                                                    * pvs_meta['pvs_static']['today']['total_eng_kwh'])
    pvs_meta['pvs_static']['today']['total_eng_kwh'] = '{:,.2f}'.format(
                                                    pvs_meta['pvs_static']['today']['total_eng_kwh'])
    
    pvs_meta['pvs_static']['this_month']['total_carbon_save'] = '{:,.1f}'.format(kWh_carbon_save_unit_kg 
                                                    * pvs_meta['pvs_static']['this_month']['total_eng_kwh'])
    pvs_meta['pvs_static']['this_month']['total_income'] = '{:,.1f}'.format(kWh_income_unit_ntd 
                                                    * pvs_meta['pvs_static']['this_month']['total_eng_kwh'])
    pvs_meta['pvs_static']['this_month']['total_eng_kwh'] = '{:,.1f}'.format(
                                                                pvs_meta['pvs_static']['this_month']['total_eng_kwh'])

    pvs_meta['pvs_static']['until_now']['total_carbon_save'] = '{:,.0f}'.format(kWh_carbon_save_unit_kg 
                                                    * pvs_meta['pvs_static']['until_now']['total_eng_kwh'])
    pvs_meta['pvs_static']['until_now']['total_income'] = '{:,.0f}'.format(kWh_income_unit_ntd 
                                                    * pvs_meta['pvs_static']['until_now']['total_eng_kwh'])
    pvs_meta['pvs_static']['until_now']['total_eng_kwh'] = '{:,.0f}'.format(
                                                    pvs_meta['pvs_static']['until_now']['total_eng_kwh'])

    logger.info('pvs_meta: %s' %  str(pvs_meta))
    return HttpResponse(json.dumps(pvs_meta))

def query_chart_data(request,data_type=PVSChartsDataTypeEnum.PVS_AMCHARTS_DAILY_ENERGY_n_VISIBILITY.value):
    '''
    Web Application API
    provide page chart display data
    current supported chart data type:
        PVS_AMCHARTS_DAILY_ENERGY_n_VISIBILITY
        PVS_AMCHARTS_HOURLY_ENERGY_n_VISIBILITY
    '''
    logger.info('query_chart_data(request,{data_type})'.format(data_type = data_type))
    try:
        data_type = int(data_type)
    except:
        logger.warning('unknow param data_type {data_type}.'.format(data_type=data_type))
        return HttpResponse('')
    
    #-> add energy value
    if data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_DAILY_ENERGY_n_VISIBILITY.value:
        pvi_query_info_type = PVIQueryInfo.Energy_Daily_List
    elif data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_HOURLY_ENERGY_n_VISIBILITY.value:
        pvi_query_info_type = PVIQueryInfo.Energy_Hourly_List
    else:
        logger.warning('unknow param data_type {data_type}.'.format(data_type=data_type))
        return HttpResponse('')
        
    pvi_dataset = {}
    pvi_list = get_pvi_list_from_settings()
    logger.info('query_for_amchart for pvi %d chart %s data' % (data_type,str(pvi_list)))
    for name in pvi_list:
        pvi_type = get_pvi_type(name)
        dataset = query_pvi_info(name, pvi_type, pvi_query_info_type)
        pvi_dataset[name] = dataset
    
    data_resp = {} #-> datetime as key
    '''
    data_resp template
    {
        '%Y-%m-%d' : {
                        'date' : '%Y-%m-%d',
                        'energy' : energy_value,
                        'visibility' : visibility_value,
                    }
    }
    '''
    if data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_DAILY_ENERGY_n_VISIBILITY.value:
        t_key_format = '%Y-%m-%d'
    elif data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_HOURLY_ENERGY_n_VISIBILITY.value:
        t_key_format = '%Y-%m-%d %H:00:00'

    for name, dataset in pvi_dataset.items():
        for entry in dataset:
            t_datetime = entry[0]
            t_key = t_datetime.strftime(t_key_format)
            t_value = entry[1]
            if t_key in data_resp.keys():
                data_resp[t_key]['energy'] += t_value
            else:
                data_resp[t_key] = {
                                    'date' : t_key,
                                    'energy' : t_value,
                                    'visibility' : 'N/A',
                                    }
    #-> add visibility
    if data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_DAILY_ENERGY_n_VISIBILITY.value:
        env_dataset = accuweather_api.query_daily_condition(CurrConditionType.Visibility)
    elif data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_HOURLY_ENERGY_n_VISIBILITY.value:
        env_dataset = accuweather_api.query_hourly_condition(CurrConditionType.Visibility)
    else:
        env_dataset = []
        logger.error('unknow param data_type {data_type}.'.format(data_type=data_type))
        
    for entry in env_dataset:
        t_datetime = entry[0]
        t_key = t_datetime.strftime(t_key_format)
        t_value = entry[1]
        if t_key in data_resp.keys():
            data_resp[t_key]['visibility'] = t_value
    
    #-> sort by date
    date_list = list(data_resp.keys())
    date_list.sort(key = lambda x : x)
    resp_content = [data_resp[t_date] for t_date in date_list]
    
    return HttpResponse(json.dumps(resp_content,indent=4))
        


        
        
