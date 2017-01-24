from django.http import HttpResponse, Http404
from django.shortcuts import redirect

from enum import Enum
from datetime import datetime

from pvappengine import PVSChartsDataTypeEnum
import pvappengine
from pvi.views import query_pvi_info
from pvi import *
import pvi
import accuweather.views as accuweather_api
from accuweather import CurrConditionType
from dbconfig.views import get_app_json_db_config

import logging, json
import accuweather
logger = logging.getLogger(__name__)

db_config = get_app_json_db_config('pvappengine', pvappengine.DEFAULT_DB_CONFIG)
kWh_carbon_save_unit_kg = db_config['kWh_carbon_save_unit_kg']
kWh_income_unit_ntd = db_config['kWh_income_unit_ntd']
HOURLY_TIME_FORMAT = '%Y-%m-%d %H:00:00'
DAILY_TIME_FORMAT = '%Y-%m-%d'

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
    db_config = get_app_json_db_config('pvi', pvi.DEFAULT_DB_CONFIG)
    return [entry['name'] for entry in db_config]

def get_pvi_type(pvi_name):
    '''
    string mapping for element in PVI_TYPE_LIST to PVIType
    '''
    db_config = get_app_json_db_config('pvi', pvi.DEFAULT_DB_CONFIG)
    for entry in db_config:
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
    response = HttpResponse(json.dumps(pvs_meta))
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = 0
    return response

def get_hourly_pvs_energy_dataset():
    """return a list of hourly [(datetime,energy),...] for all pvs inverters"""
    pvi_list = get_pvi_list_from_settings()
    pvi_dataset = {}
    for name in pvi_list:
        pvi_type = get_pvi_type(name)
        dataset = query_pvi_info(name, pvi_type, PVIQueryInfo.Energy_Hourly_List)
        pvi_dataset[name] = dataset

    pvs_dataset = {}
    for name, dataset in pvi_dataset.items():
        for entry in dataset:
            t_datetime = entry[0]
            t_key = t_datetime.strftime(HOURLY_TIME_FORMAT)
            t_value = entry[1]
            if t_key in pvs_dataset.keys():
                pvs_dataset[t_key]['energy'] += t_value
            else:
                pvs_dataset[t_key] = {'date' : datetime.strptime(t_key,HOURLY_TIME_FORMAT),
                                    'energy' : t_value,}
    dataset = [[entry['date'],entry['energy']] for _, entry in pvs_dataset.items()]
    dataset.sort(key = lambda x: x[0])
    return dataset

def get_daily_pvs_energy_dataset():
    """return a list of daily [(datetime,energy)...] for all pvs inverters"""
    pvi_list = get_pvi_list_from_settings()
    pvi_dataset = {}
    for name in pvi_list:
        pvi_type = get_pvi_type(name)
        dataset = query_pvi_info(name, pvi_type, PVIQueryInfo.Energy_Daily_List)
        pvi_dataset[name] = dataset

    pvs_dataset = {}
    for name, dataset in pvi_dataset.items():
        for entry in pvs_dataset:
            t_datetime = entry[0]
            t_key = t_datetime.strftime(DAILY_TIME_FORMAT)
            t_value = entry[1]
            if t_key in pvs_dataset.keys():
                pvs_dataset[t_key]['energy'] += t_value
            else:
                pvs_dataset[t_key] = {'date' : datetime.strptime(t_key,DAILY_TIME_FORMAT),
                                    'energy' : t_value,}
    dataset = [[entry['date'],entry['energy']] for _, entry in pvs_dataset.items()]
    dataset.sort(key = lambda x: x[0])
    return dataset
    
def combine_dataset(time_format,**kwargs):
    """return a list of [{date:datetime,key:value,...}...]"""
    t_dataset = {}
    for key in kwargs:
        for entry in kwargs[key]:
            t_key = entry[0].strftime(time_format)
            if t_key in t_dataset.keys():
                t_dataset[t_key][key] = entry[1]
            else:
                t_dataset[t_key] = {'date': t_key,
                                    key: entry[1]}
    return t_dataset

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
    elif data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_HOURLY_ENERGY_VISIBILITY_UV.value:
        #-> get hourly pvs energy dataset
        pvs_dataset = get_hourly_pvs_energy_dataset()
        logger.debug('pvs_dataset: ' + str(pvs_dataset))
        #-> get hourly max env visibility dataset
        visibility_dataset = accuweather_api.query_hourly_condition(CurrConditionType.Visibility)
        logger.debug('visibility_dataset: ' + str(visibility_dataset))
        #-> get hourly max env uv index dataset
        uv_dataset = accuweather_api.query_hourly_condition(CurrConditionType.UV_Index)
        logger.debug('uv_dataset: ' + str(uv_dataset))
        #-> combine all dataset
        t_dataset = combine_dataset(HOURLY_TIME_FORMAT,
                                    energy = pvs_dataset,
                                    visibility = visibility_dataset,
                                    uv = uv_dataset)
        logger.debug('combine_dataset: ' + str(t_dataset))
        #-> sort by date
        date_list = list(t_dataset.keys())
        date_list.sort(key = lambda x : x)
        resp_content = [t_dataset[t_date] for t_date in date_list]
        
        response = HttpResponse(json.dumps(resp_content,indent=4))
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = 0
        return response
    else:
        logger.warning('unknow param data_type {data_type}.'.format(data_type=data_type))
        return HttpResponse('')
        
    pvi_dataset = {}
    pvi_list = get_pvi_list_from_settings()
    logger.debug('pvi_list: %s' % str(pvi_list))
    for name in pvi_list:
        pvi_type = get_pvi_type(name)
        logger.debug('pvi name: %s, type: %s' % (name, PVIType(pvi_type).name))
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
    
    response = HttpResponse(json.dumps(resp_content,indent=4))
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = 0
    return response
        
def clean_db(request,table_name=None):
    if table_name is None:
        table_name = 'all'
        pvi.models.RegData.objects.all().delete()
        pvi.models.EnergyData.objects.all().delete()
        accuweather.models.CurrConditions.objects.all().delete()
    elif table_name == 'pvi_regdata':
        pvi.models.RegData.objects.all().delete()
    elif table_name == 'pvi_energydata':
        pvi.models.EnergyData.objects.all().delete()
    elif table_name == 'accuweather_currconditions':
        accuweather.models.CurrConditions.objects.all().delete()
    else:
        raise Http404
    
    return HttpResponse('DB %s tables are purged' % table_name)

from pvi.views import do_action_on_pvs, action_load_pvi_eng_history
def init_db(request):
    do_action_on_pvs(
        get_app_json_db_config('pvi', pvi.DEFAULT_DB_CONFIG),
        action_load_pvi_eng_history)    
    return HttpResponse('PVS Energy History Loaded')        
        
