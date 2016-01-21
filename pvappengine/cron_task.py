#!/usr/bin/env python

from django.conf import settings
import os, sys, django, logging

logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    sys_path_to_add = r'D:\lee_shiueh\FLH\workspace\pvstation\pvappengine'
else:
    sys_path_to_add = '/home/pi/pvappengine'
#sys_path_to_add = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.append(sys_path_to_add)

os.environ['DJANGO_SETTINGS_MODULE'] = 'pvappengine.settings'
django.setup()
    
try:
    from pvi.h5 import controller as h5_controller
    h5_controller.save_all_pvi_input_register_value()
    logger.info('h5_controller.save_all_pvi_input_register_value executed')

    from accuweather.models import CurrConditions
    CurrConditions.save_current_location_condition(settings.PVS_CONFIG['accuweather']['locationkey'])
    logger.info('CurrConditions.save_current_location_condition executed')

except:
    logger.error('except', exc_info=True)

