
import os
import logging

logger = logging.getLogger(__name__)

def get_pi_cpuinfo():
    '''return raspberry pi json data from /proc/cpuinfo:
    {
        'hardware' : 'xxx',
        'revision': 'xxx',
        'serial' : 'xxx',
    } 
    '''
    if os.path.exists('/proc/cpuinfo'):
        cpuinfo = {}
        with open('/proc/cpuinfo') as fh:
            for info in fh:
                if fh.starts_with('Hardware'):
                    cpuinfo['hardware'] = (info.split(':')[-1]).strip()
                if fh.starts_with('Revision'):
                    cpuinfo['revision'] = (info.split(':')[-1]).strip()
                if fh.starts_with('Serial'):
                    cpuinfo['serial'] = (info.split(':')[-1]).strip()
        logger.debug('current cpuinfo: %s' % str(cpuinfo))            
        return cpuinfo
    else:
        logger.warning('no /proc/cpuinfo file exist!')
        return None