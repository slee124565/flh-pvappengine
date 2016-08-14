#!/usr/bin/env python

import os, sys, django, logging

logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    sys_path_to_add = r'D:\lee_shiueh\FLH\workspace\django_apps\pvappengine'
else:
    sys_path_to_add = '/usr/share/pvappengine'
#sys_path_to_add = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.append(sys_path_to_add)

os.environ['DJANGO_SETTINGS_MODULE'] = 'pvappengine.settings'
django.setup()

from dbconfig.views import get_app_json_db_config
import accuweather
    
try:
    from accuweather.models import CurrConditions
    accu_dbconfig = get_app_json_db_config('accuweather', accuweather.DEFAULT_DB_CONFIG)
    CurrConditions.save_current_location_condition(accu_dbconfig['locationkey'],
                                                   accu_dbconfig['apikey'])
    logger.info('CurrConditions.save_current_location_condition executed')
    
    from pvi.h5 import controller as h5_controller
    h5_controller.check_n_set_measurement_index()
    h5_controller.save_all_pvi_input_register_value()
    logger.info('h5_controller.save_all_pvi_input_register_value executed')

    import pvi.views
    import accuweather.views
    pvi.views.clear_expired_records()
    accuweather.views.clear_expired_records()

except:
    logger.error('except', exc_info=True)

