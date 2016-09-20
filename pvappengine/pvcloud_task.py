from django.core import signing

import logging
logger = logging.getLogger(__name__)

from dbconfig.models import AppOption
from pi import get_pi_cpuinfo

import requests
import urllib

PVCLOUD_URL = 'https://server-dot-solar-cloud-143410.appspot.com'
PVCLOUD_REPORT_URL = PVCLOUD_URL + '/pvs/report/'

def pvcloud_report_v1():
    '''implement pvstation client report to pvcloud server function
    post encrypted json data for pvcloud web api
    ::
    
    {
        'version': 'v1',
        'cpuinfo': { 
                    'hardware': 'xxx',
                    'revision': 'xxx',
                    'serial': 'xxx',
                     },
        'dbconfig' : {
                    'pvi': '<json data>',
                    'accuweather': '<json data>'
                     },
    }
    '''
    dbconfig = {}
    entry = AppOption.objects.get(app_name = 'pvi')
    dbconfig['pvi'] = entry.json_data
    entry = AppOption.objects.get(app_name = 'accuweather')
    dbconfig['accuweather'] = entry.json_data
    
    report_data = {'version': 'v1'}
    report_data['cpuinfo'] = get_pi_cpuinfo()
    report_data['dbconfig'] = dbconfig
    
    encrypt_report = signing.dumps(report_data)

    #logging.debug('report url: %s' % PVCLOUD_REPORT_URL)    
    r = requests.post(PVCLOUD_REPORT_URL,data={'data': encrypt_report})
    logging.debug('pvcloud_report_v1 response status code %s and data:\n%s' % (r.status_code,
                                                                              r.text))
    if r.status_code == 200:
        print(r.text)
        return True
    else:
        logging.warning('pvcloud_report_v1 http post failed!')
        return False
    
