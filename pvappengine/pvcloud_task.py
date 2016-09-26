from django.core import signing
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

from dbconfig.models import AppOption
from dbconfig.views import get_app_json_db_config
from pi import get_pi_cpuinfo, PiCpuInfo

import requests
import json

PVCLOUD_URL = 'https://server-dot-solar-cloud-143410.appspot.com'
#PVCLOUD_URL = 'http://104.199.209.26:8000'
PVCLOUD_REPORT_URL = PVCLOUD_URL + '/pvs/report/'
PVCLOUD_DBCONFIG_URL = PVCLOUD_URL + '/pvs/dbconfig/'

class PVSDBConfig:
    pvi = None
    accuweather = None
    
    def __init__(self):
        self.pvi = get_app_json_db_config('pvi', '{}')
        self.accuweather = get_app_json_db_config('accuweather', '{}')
    
    def __call__(self):
        return {
                'pvi': self.pvi,
                'accuweather': self.accuweather
                }
    
class PVCloudReport:
    version = 'v1.1'
    local_ip = '127.0.0.1'
    cpuinfo = None
    dbconfig = None
    
    def __init__(self,cpuinfo,dbconfig):
        self.cpuinfo = cpuinfo
        self.dbconfig = dbconfig
        
    def __call__(self):
        return { 
                'version': 'v1.1',
                'local_ip': self.local_ip,
                'cpuinfo': self.cpuinfo() if callable(self.cpuinfo) else self.cpuinfo,
                'dbconfig': self.dbconfig() if callable(self.dbconfig) else self.dbconfig,
                }

def pvcloud_report_v1_1():
    '''implement pvstation client report to pvcloud server function
    post encrypted json data for pvcloud web api
    ::
    
    {
        'version': 'v1.1',
        'local_ip': 'xxx.xxx.xxx.xxx',
        'cpuinfo': { 
                    'hardware': 'xxx',s
                    'revision': 'xxx',
                    'serial': 'xxx',
                     },
        'dbconfig' : {
                    'pvi': '<json data>',
                    'accuweather': '<json data>'
                     },
    }
    '''
    try:
        pvcloud_report = PVCloudReport(PiCpuInfo(),PVSDBConfig())
        logger.debug('pvcloud_report v1.1:\n%s' % str(pvcloud_report()))
        
        encrypt_report = signing.dumps(pvcloud_report)
    
        #logging.debug('report url: %s' % PVCLOUD_REPORT_URL)
        PVCLOUD_REPORT_URL_V1_1 = PVCLOUD_REPORT_URL + 'v1_1/'    
        r = requests.post(PVCLOUD_REPORT_URL_V1_1,data={'data': encrypt_report})
        logger.debug('pvcloud_report_v1 response status code %s and data:\n%s' % (r.status_code,
                                                                                  r.text))
        if r.status_code == 200:
            print(r.text)
            return True
        else:
            print('pvcloud_report_v1 http post failed, check log file!')
            logger.warning('pvcloud_report_v1 http post failed!')
            return False
    except:
        logger.error('pvcloud_report_v1_1 fail!', exc_info=True)
        return False
        
def pvcloud_report_v1():
    '''implement pvstation client report to pvcloud server function
    post encrypted json data for pvcloud web api
    ::
    
    {
        'version': 'v1',
        'cpuinfo': { 
                    'hardware': 'xxx',s
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
    if not entry is None:
        dbconfig['pvi'] = json.loads(entry.json_data)
    entry = AppOption.objects.get(app_name = 'accuweather')
    if not entry is None:
        dbconfig['accuweather'] = json.loads(entry.json_data)
    
    report_data = {'version': 'v1'}
    report_data['cpuinfo'] = get_pi_cpuinfo()
    report_data['dbconfig'] = dbconfig
    
    encrypt_report = signing.dumps(report_data)

    #logging.debug('report url: %s' % PVCLOUD_REPORT_URL)    
    r = requests.post(PVCLOUD_REPORT_URL,data={'data': encrypt_report})
    logger.debug('pvcloud_report_v1 response status code %s and data:\n%s' % (r.status_code,
                                                                              r.text))
    if r.status_code == 200:
        print(r.text)
        return True
    else:
        print('pvcloud_report_v1 http post failed, check log file!')
        logger.warning('pvcloud_report_v1 http post failed!')
        return False

def pvcloud_dbconfig_v1():
    '''implement the client site for pvcloud dbconfig web api
    1. query (http get) pvcloud if there is dbconfig exist
    with querystring sserial=<signed([pi_seria-timestamp])>
    2. update database dbconfig if new config exist
    3. ack (http post) for pvcloud about config updated
    with payload 
    { 'config_id' = 'xxx', 'serial': '<pi_serial>', 'result':'pass|fail' }
    to signed as
    { 'data': <signed_payload> }
    '''
    pi_serial = get_pi_cpuinfo().get('serial','')

    sserial = signing.dumps([pi_serial + '-' + datetime.now().strftime('%Y%m%d%H%M%S')])
    r = requests.get(PVCLOUD_DBCONFIG_URL,params={'sserial': sserial})
    
    if r.status_code == 200:
        resp_content = signing.loads(r.text)
        print('dbconfig query result: \n%s' % json.dumps(resp_content,indent=2))
        
        if resp_content.get('config_id',None) is None:
            logger.debug('no new dbconfig entry from pvcloud')
            return
    else:
        logger.warning('dbconfig query fail!')
        return
        
    new_dbconfig = resp_content.get('data',None)
    if new_dbconfig is None:
        logger.warning('no new dbconfig data exist')
        return
    #logger.debug('received dbconfig: \n%s' % json.dumps(new_dbconfig,indent=2))
    
    for key in new_dbconfig:
        entry = AppOption.objects.get(app_name=key)
        if entry is None:
            logger.warning('dbconfig key (%s) not exist in appoption table' % key)
        else:
            old_value = entry.json_data
            new_value = json.dumps(new_dbconfig[key])
            entry.json_data = new_value
            entry.save()
            logger.info('new appoption key (%s) update from %s to %s' % (key,
                                                                         old_value,
                                                                         new_value))
    
    
    payload = {'config_id': resp_content.get('config_id'),
               'serial': pi_serial,
               'result': 'pass',
               }
    logger.debug('origin payload data: \n%s' % str(payload))
    
    r = requests.post(PVCLOUD_DBCONFIG_URL,data={'data' : signing.dumps(payload)})
    if r.status_code == 200:
        print(r.text)
        return True
    else:
        logger.warning('pvcloud_dbconfig_v1 post result fail!')
        print('pvcloud_dbconfig_v1 post result fail!')
        return False
    
        
        
        
        
        
