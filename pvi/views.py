from django.shortcuts import render
from datetime import datetime, date

from pvi import PVIType, PVIQueryInfo
from pvi.h5 import controller as h5_controller\
from pvi.models import RegData

import logging
logger = logging.getLogger(__name__)
    
def query_pvi_info(pvi_name,pvi_type=PVIType.Delta_PRI_H5,query_info=PVIQueryInfo.Energy_Today):
    '''
    return a list of [[datetime,valule],...] information for pvi_name
    '''
    if (pvi_name is None) or (pvi_name == ''):
        logger.error('query_pvi_info for all pvi is not implemented yet.')
        return None
    
    if pvi_type == PVIType.Delta_PRI_H5:
        return h5_controller.query_pvi_info(pvi_name,query_info)
    else:
        logger.error('unknow pvi type %s from name %s' % (pvi_type,pvi_name))
            
def clear_expired_records():
    expired_date = date(date.today().year-1,1,1)
    count, _ = RegData.objects.filter(prob_date__lt = expired_date).delete()
    if count > 0:
        logger.info('clear expired records %d' % count)
    else:
        logger.debug('no expired %s records' % str(expired_date))
    