#!/usr/bin/env python

import os, sys, django

os.environ['DJANGO_SETTINGS_MODULE'] = 'pvappengin_local.settings'
sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))
django.setup()

from pvi.h5 import controller as h5_controller

h5_controller.save_all_pvi_input_register_value()