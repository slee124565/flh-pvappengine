#!/root/Env/appeng/bin/python

import os, sys, django
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print('pvappengine project root: %s' % proj_root)
sys.path.append(proj_root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'pvappengine.settings'
django.setup()

from pvappengine.pvcloud_task import *

#pvcloud_report_v1()
#pvcloud_dbconfig_v1()
pvcloud_report_v1_1()
