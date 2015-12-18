#!/usr/bin/env python

import os, sys, django

sys_path_to_add = '/home/pi/pvappengine'
#sys_path_to_add = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.append(sys_path_to_add)

os.environ['DJANGO_SETTINGS_MODULE'] = 'pvappengine.settings'
django.setup()

from pvi.h5 import controller as h5_controller
h5_controller.save_all_pvi_input_register_value()
