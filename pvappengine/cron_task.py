#!/root/Env/appeng/bin/python

import os, sys, django, logging
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)
logger.debug('pvappengine project root path: %s' % proj_root)
sys.path.append(proj_root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'pvappengine.settings'
django.setup()

from dbconfig.views import get_app_json_db_config
import accuweather
import pvi
    
try:
    from accuweather.models import CurrConditions
    accu_dbconfig = get_app_json_db_config('accuweather', accuweather.DEFAULT_DB_CONFIG)
    CurrConditions.save_current_location_condition(accu_dbconfig['locationkey'],
                                                   accu_dbconfig['apikey'])
    logger.info('CurrConditions.save_current_location_condition executed')
    
    #from pvi.h5 import controller as h5_controller
    #h5_controller.check_n_set_measurement_index()
    #h5_controller.save_all_pvi_input_register_value()
    from pvi.views import save_all_pvi_input_register_value
    save_all_pvi_input_register_value(get_app_json_db_config('pvi', pvi.DEFAULT_DB_CONFIG))
    logger.info('h5_controller.save_all_pvi_input_register_value executed')

    import pvi.views
    import accuweather.views
    pvi.views.clear_expired_records()
    accuweather.views.clear_expired_records()

except:
    logger.error('except', exc_info=True)

