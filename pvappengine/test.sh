#!/root/Env/appeng/bin/python

import os, sys, django, json
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print('pvappengine project root: %s' % proj_root)
sys.path.append(proj_root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'pvappengine.settings'
django.setup()

from pvappengine.pvcloud_task import *
from pi import *

#pvcloud_report_v1()
#pvcloud_dbconfig_v1()
#pvcloud_report_v1_1()
#print('get_local_ip:' + str(get_local_ip()))
#http_report = HTTPReportToPVCloud_v1_2()
#print(json.dumps(http_report.pvcloud_report(),indent=2))

report = HTTPReportToPVCloud_v1_2()
report()