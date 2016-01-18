from django.shortcuts import render
from datetime import datetime

from pvi import PVIType, PVIQueryInfo
from pvi.h5 import controller as h5_controller

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
            
