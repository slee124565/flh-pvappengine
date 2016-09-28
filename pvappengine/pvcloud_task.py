from django.core import signing
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

from dbconfig.models import AppOption
from dbconfig.views import get_app_json_db_config
from pi import get_pi_cpuinfo,get_local_ip, PiCpuInfo
from pvi.models import RegData
from pvi.delta_pri_h5 import INPUT_REGISTER, REGISTER_ADDRESS_COL, Register_Polling_List

import requests
import json

SERVER_USE = 3

PVCLOUD_URL_STAGING='https://staging-dot-solar-cloud-143410.appspot.com'
PVCLOUD_URL_PRODCUT='https://server-dot-solar-cloud-143410.appspot.com'
PVCLOUD_URL_TEST='http://104.199.209.26:8000'

if SERVER_USE == 1:
    PVCLOUD_URL = PVCLOUD_URL_PRODCUT
    logger.info('using production pvcloud url (%s)' % PVCLOUD_URL)
elif SERVER_USE == 2:
    PVCLOUD_URL = PVCLOUD_URL_STAGING
    logger.info('using staging pvcloud url (%s)' % PVCLOUD_URL)
else:
    PVCLOUD_URL = PVCLOUD_URL_TEST
    logger.info('using testing pvcloud url (%s)' % PVCLOUD_URL)
    
PVCLOUD_REPORT_URL = PVCLOUD_URL + '/pvs/report/'
PVCLOUD_DBCONFIG_URL = PVCLOUD_URL + '/pvs/dbconfig/'

class PVSDBConfig:
    '''query database dbconfig_appoption table with appname in [pvi,accuweather]
    and be a callable object with json data return
    '''
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

class PVEnergySyncReport:
    '''query database pvi_regdata table with sync_flag = False and
    specific (pvi_type,address) with limited rowdata
    To be a callable object with json data return
    Update sync_flag = True with database when rowdata is synced with 
    pvcloud server
    '''
    MAX_REPORT_COUNT = len(Register_Polling_List) * 1
    model_queryset = None
    
    def __init__(self):
        self.model_queryset = PVEnergySyncReport.query_unsync_regdata()
        
    @classmethod
    def query_unsync_regdata(cls):
        return RegData.objects.filter(sync_flag=False).order_by('-id')[:cls.MAX_REPORT_COUNT]
    
    @classmethod
    def map_delta_pri_h5_reg_address_to_name(cls,reg_address):
        '''only map energy_dc_life, energy_today, ac_output_voltage,
        ac_output_current, ac_output_watt
        '''
        if str(reg_address) == INPUT_REGISTER.get('DC Life Wh')[REGISTER_ADDRESS_COL]:
            return 'en_dc_life'

        if str(reg_address) == INPUT_REGISTER.get('Today Wh')[REGISTER_ADDRESS_COL]:
            return 'en_toady'

        if str(reg_address) == INPUT_REGISTER.get('Voltage')[REGISTER_ADDRESS_COL]:
            return 'voltage'
        
        if str(reg_address) == INPUT_REGISTER.get('Current')[REGISTER_ADDRESS_COL]:
            return 'current'

        if str(reg_address) == INPUT_REGISTER.get('Wattage')[REGISTER_ADDRESS_COL]:
            return 'wattage'
        
        return str(reg_address)
            
    def __call__(self):
        return [{'data_id': entry.id,
                 'create_time': entry.date.strftime('%Y-%m-%d %H:%M:%S'),
                 'pvi_name':entry.pvi_name,
                 'modbus_id':entry.modbus_id,
                 'value': entry.value,
                 'data_type': PVEnergySyncReport.map_delta_pri_h5_reg_address_to_name(entry.address),
                 'measurement_index':'grid'} for entry in self.model_queryset]
    
class PVCloudReport:
    version = 'v1.1'
    local_ip = '127.0.0.1'
    cpuinfo = None
    dbconfig = None
    
    def __init__(self,cpuinfo,dbconfig):
        self.cpuinfo = cpuinfo
        self.dbconfig = dbconfig
        self.local_ip = get_local_ip()
        
    def __call__(self):
        return { 
                'version': 'v1.1',
                'local_ip': self.local_ip,
                'cpuinfo': self.cpuinfo() if callable(self.cpuinfo) else self.cpuinfo,
                'dbconfig': self.dbconfig() if callable(self.dbconfig) else self.dbconfig,
                }

class PVCloudReport_v1_2(PVCloudReport):
    version = 'v1.2'
    energy_sync_report = None   # list of PVEnergySyncReport
    
    def __init__(self,cpuinfo,dbconfig,energy_sync_report):
        super(PVCloudReport_v1_2,self).__init__(cpuinfo, dbconfig)
        self.energy_sync_report = energy_sync_report
        
    def update_energy_report_sync(self):
        self.energy_sync_report.model_queryset.update(sync_flag=True)
        logger.debug('PVCloudReport_v1_2.update_energy_report_sync')
        
    def __call__(self):
        json_data = super(PVCloudReport_v1_2,self).__call__()
        json_data['energy'] = self.energy_sync_report() if callable(self.energy_sync_report) else self.energy_sync_report
        return json_data
            
class HTTPReportToPVCloud_v1_2:
    pvcloud_report = None
    
    def __init__(self):
        self.pvcloud_report = PVCloudReport_v1_2(PiCpuInfo(),PVSDBConfig(),PVEnergySyncReport())
    
    def __call__(self):
        try:
            report_json = self.pvcloud_report()
            encrypt_report = signing.dumps(report_json)
        
            #logging.debug('report url: %s' % PVCLOUD_REPORT_URL)
            PVCLOUD_REPORT_URL_version = PVCLOUD_REPORT_URL + self.pvcloud_report.version.replace('.','_') + '/'   
            logger.debug('pvcloud url %s' % PVCLOUD_REPORT_URL_version)
            r = requests.post(PVCLOUD_REPORT_URL_version,data={'data': encrypt_report})
            logger.debug('%s response status code %s and data:\n%s' % (
                                                                       self.__class__.__name__,
                                                                       r.status_code,
                                                                       r.text))
            if r.status_code == 200:
                print(r.text)
                logger.info('call HTTPReportToPVCloud_v1_2 object success')
                self.pvcloud_report.update_energy_report_sync()
                return True
            else:
                logger.warning('%s get error http response code %s!' % (self.__class__.__name__,
                                                                        r.status_code))
                return False
        except:
            logger.error('%s fail!' % self.__class__.__name__, exc_info=True)
            return False
    
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
        
        encrypt_report = signing.dumps(pvcloud_report())
    
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
    
        
        
        
        
        
