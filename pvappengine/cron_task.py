#!/root/Env/appeng/bin/python

import os, sys, django
import time, random
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

time.sleep(random.randrange(1,10))

#print('pvappengine project root: %s' % proj_root)
sys.path.append(proj_root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'pvappengine.settings'
django.setup()

from dbconfig.views import get_app_json_db_config
import accuweather
import pvi
    
from accuweather.models import CurrConditions
accu_dbconfig = get_app_json_db_config('accuweather', accuweather.DEFAULT_DB_CONFIG)
CurrConditions.save_current_location_condition(accu_dbconfig['locationkey'],
                                               accu_dbconfig['apikey'])
print('CurrConditions.save_current_location_condition executed')

from pvappengine.pvcloud_task import pvcloud_report_v1, pvcloud_dbconfig_v1
pvcloud_report_v1()
time.sleep(random.randrange(1,5))
pvcloud_dbconfig_v1()
print('pvcloud_report executed')

from pvi.views import save_all_pvi_input_register_value
save_all_pvi_input_register_value(get_app_json_db_config('pvi', pvi.DEFAULT_DB_CONFIG))
print('h5_controller.save_all_pvi_input_register_value executed')

import accuweather.views
pvi.views.clear_expired_records()
accuweather.views.clear_expired_records()



