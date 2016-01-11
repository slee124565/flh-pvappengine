from django.http import HttpResponse
from pvi.models import RegData

from pvi.views import query_pvi_info
from pvi import PVIQueryInfo, PVIEnvConditions
import accuweather.views as accuweather_api
from accuweather import CurrConditionType

import logging, json
logger = logging.getLogger(__name__)

#-> TODO: get pvi name list from database or django settings
pvi_list = ['H5']
kWh_carbon_save_unit_kg = 0.637
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
    pvs_meta['pvs_static']['today']['total_eng_kwh'] += round(0.001 * query_pvi_info(pvi_name, 
                                                                  query_info=PVIQueryInfo.Energy_Today),3)
    
    pvs_meta['pvs_static']['this_month']['total_eng_kwh'] += round(0.001 * query_pvi_info(pvi_name, 
                                                                  query_info=PVIQueryInfo.Energy_This_Month),3)

    pvs_meta['pvs_static']['until_now']['total_eng_kwh'] += round(0.001 * query_pvi_info(pvi_name, 
                                                                  query_info=PVIQueryInfo.Energy_Until_Now),3)
    
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
        
        