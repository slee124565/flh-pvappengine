from django.http import HttpResponse
from enum import Enum

from pvappengine import PVSChartsDataTypeEnum
from pvi.views import query_pvi_info
from pvi import PVIQueryInfo
import accuweather.views as accuweather_api
from accuweather import CurrConditionType

import logging, json
logger = logging.getLogger(__name__)

#-> TODO: get pvi name list from database or django settings
pvi_list = ['H5']
kWh_carbon_save_unit_kg = 0.637
#TODO: kWh_income_unit_ntd should be configurable by user
kWh_income_unit_ntd = 6.8633


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
def add_pvi_info_into_pvs_meta(pvi_name):
    t_value = query_pvi_info(pvi_name,query_info=PVIQueryInfo.Energy_Today)
    if not t_value is None:
        pvs_meta['pvs_static']['today']['total_eng_kwh'] += round(0.001 * t_value, 3)
    
    t_value = query_pvi_info(pvi_name,query_info=PVIQueryInfo.Energy_This_Month)
    if not t_value is None:
        pvs_meta['pvs_static']['this_month']['total_eng_kwh'] += round(0.001 * t_value, 3)

    t_value = query_pvi_info(pvi_name,query_info=PVIQueryInfo.Energy_Until_Now)
    if not t_value is None:
        pvs_meta['pvs_static']['until_now']['total_eng_kwh'] += round(0.001 * t_value, 3)
    
    if not pvi_name in pvs_meta['dc_output'].keys():
        pvs_meta['dc_output'][pvi_name] = {
                                           'voltage': 'N/A',
                                           'current': 'N/A',
                                           'wattage': 'N/A',
                                           }
    voltage = query_pvi_info(pvi_name,query_info=PVIQueryInfo.AC_Output_Voltage)
    if not (voltage is None):
        pvs_meta['dc_output'][pvi_name]['voltage'] = round(voltage,1)

    current = query_pvi_info(pvi_name,query_info=PVIQueryInfo.AC_Output_Current)
    if not (current is None):
        pvs_meta['dc_output'][pvi_name]['current'] = round(current,2)

    wattage = query_pvi_info(pvi_name,query_info=PVIQueryInfo.AC_Output_Wattage)
    if not (wattage is None):
        pvs_meta['dc_output'][pvi_name]['wattage'] = wattage

def add_environment_condition_into_pvs_meta():
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
    
    if pvi_name is None:
        # TODO: need to verify for multiple pvi pvstation
        logger.info('query_pvs_meta for all pvi')
        for name in pvi_list:
            add_pvi_info_into_pvs_meta(name)
    else:
        logger.info('query_pvs_meta for pvi %s' % pvi_name)
        add_pvi_info_into_pvs_meta(pvi_name)
        
    add_environment_condition_into_pvs_meta()
    pvs_meta['pvs_static']['today']['total_carbon_save'] = round(kWh_carbon_save_unit_kg 
                                                                 * pvs_meta['pvs_static']['today']['total_eng_kwh'],
                                                                 3)
    pvs_meta['pvs_static']['today']['total_income'] = round(kWh_income_unit_ntd 
                                                            * pvs_meta['pvs_static']['today']['total_eng_kwh'],
                                                            4)
    
    pvs_meta['pvs_static']['this_month']['total_carbon_save'] = round(kWh_carbon_save_unit_kg 
                                                    * pvs_meta['pvs_static']['this_month']['total_eng_kwh'],
                                                    3)
    pvs_meta['pvs_static']['this_month']['total_income'] = round(kWh_income_unit_ntd 
                                                    * pvs_meta['pvs_static']['this_month']['total_eng_kwh'],
                                                    4)

    pvs_meta['pvs_static']['until_now']['total_carbon_save'] = round(kWh_carbon_save_unit_kg 
                                                    * pvs_meta['pvs_static']['until_now']['total_eng_kwh'],
                                                    3)
    pvs_meta['pvs_static']['until_now']['total_income'] = round(kWh_income_unit_ntd 
                                                    * pvs_meta['pvs_static']['until_now']['total_eng_kwh'],
                                                    4)

    logger.info('pvs_meta: %s' %  str(pvs_meta))
    return HttpResponse(json.dumps(pvs_meta))

def query_chart_data(request,pvi_name='',data_type=PVSChartsDataTypeEnum.PVS_AMCHARTS_DAILY_ENERGY_n_VISIBILITY):
    '''
    Web Application API
    provide page chart display data
    [pvi_name == None or pvi_name == ''] means query for all pv inverter (pv station)
    '''
    logger.info('query_chart_data(request,{pvi_name},{data_type})'.format(pvi_name = pvi_name,
                                                                          data_type = data_type))
    #-> add energy value
    if data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_DAILY_ENERGY_n_VISIBILITY:
        pvi_query_info_type = PVIQueryInfo.Energy_Daily_List
    elif data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_HOURLY_ENERGY_n_VISIBILITY:
        pvi_query_info_type = PVIQueryInfo.Energy_Hourly_List
        
    pvi_dataset = {}
    if pvi_name is None or pvi_name == '':
        logger.info('query_for_amchart for pvi %s chart %s data' % (data_type,str(pvi_list)))
        for name in pvi_list:
            dataset = query_pvi_info(name, pvi_query_info_type)
            pvi_dataset[name] = dataset
    else:
        logger.info('query_for_amchart for pvi %s chart %s data' % (pvi_name,data_type))
        dataset = query_pvi_info(pvi_name, pvi_query_info_type)
        pvi_dataset[pvi_name] = dataset
    
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
    if data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_DAILY_ENERGY_n_VISIBILITY:
        t_key_format = '%Y-%m-%d'
    elif data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_HOURLY_ENERGY_n_VISIBILITY:
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
    if data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_DAILY_ENERGY_n_VISIBILITY:
        env_dataset = accuweather_api.query_daily_condition(CurrConditionType.Visibility)
    elif data_type == PVSChartsDataTypeEnum.PVS_AMCHARTS_HOURLY_ENERGY_n_VISIBILITY:
        env_dataset = accuweather_api.query_hourly_condition(CurrConditionType.Visibility)
        
    for entry in env_dataset:
        t_datetime = entry[0]
        t_key = t_datetime.strftime(t_key_format)
        t_value = entry[1]
        if t_key in data_resp.keys():
            data_resp[t_key]['visibility'] = t_value
        else:
            data_resp[t_key] = {
                                'date' : t_key,
                                'energy' : 'N/A',
                                'visibility' : t_value,
                                }
    
    #-> sort by date
    date_list = list(data_resp.keys())
    date_list.sort(key = lambda x : x)
    resp_content = [data_resp[t_date] for t_date in date_list]
    return HttpResponse(json.dumps(resp_content,indent=4))
        


        
        
