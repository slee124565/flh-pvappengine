
import os
import logging
from subprocess import check_output
from sys import exc_info

logger = logging.getLogger(__name__)

class PiCpuInfo:
    hardware = ''
    revision = ''
    serial = ''
    
    def __call__(self):
        '''return raspberry pi json data from /proc/cpuinfo:
        {
            'hardware' : 'xxx',
            'revision': 'xxx',
            'serial' : 'xxx',
        } 
        '''
        try:
            with open('/proc/cpuinfo') as fh:
                for info in fh:
                    if info.startswith('Hardware'):
                        self.hardware = (info.split(':')[-1]).strip()
                    if info.startswith('Revision'):
                        self.revision = (info.split(':')[-1]).strip()
                    if info.startswith('Serial'):
                        self.serial = (info.split(':')[-1]).strip()
            return {'hardware': self.hardware,
                    'revision': self.revision,
                    'serial': self.serial}
        except:
            logger.error('get_pi_cpuinfo fail', exc_info=True)
            return None

def get_pi_cpuinfo():
    '''return raspberry pi json data from /proc/cpuinfo:
    {
        'hardware' : 'xxx',
        'revision': 'xxx',
        'serial' : 'xxx',
    } 
    '''
    try:
        if os.path.exists('/proc/cpuinfo'):
            cpuinfo = {}
            with open('/proc/cpuinfo') as fh:
                for info in fh:
                    if info.startswith('Hardware'):
                        cpuinfo['hardware'] = (info.split(':')[-1]).strip()
                    if info.startswith('Revision'):
                        cpuinfo['revision'] = (info.split(':')[-1]).strip()
                    if info.startswith('Serial'):
                        cpuinfo['serial'] = (info.split(':')[-1]).strip()
            logger.debug('current cpuinfo: %s' % str(cpuinfo))            
            return cpuinfo
        else:
            logger.warning('no /proc/cpuinfo file exist!')
            return None
    except:
        logger.error('get_pi_cpuinfo fail', exc_info=True)
        return {}
    
def get_local_ip():
    '''return local ip address'''
    try:
        local_ip = check_output(['hostname', '-I'])
        logger.debug('current local ip address %s' & local_ip)
        return local_ip
    except:
        logger.warning('get_local_ip fail', exc_info=True)
        return ''