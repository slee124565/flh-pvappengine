from django.shortcuts import render
from datetime import datetime

from pvi import PVIType, PVIQueryInfo
from pvi.h5 import controller as h5_controller

import logging
logger = logging.getLogger(__name__)

def get_pvi_type_by_name(pvi_name):
    # TODO: query database for result
    if pvi_name in ['H5']:
        return PVIType.Delta_PRI_H5
    else:
        return None
    
def query_pvi_info(pvi_name,query_info=PVIQueryInfo.Energy_Today):
    if (pvi_name is None) or (pvi_name == ''):
        logger.error('query_pvi_info for all pvi is not implemented yet.')
    else:
        pvi_type = get_pvi_type_by_name(pvi_name)
        if pvi_type == PVIType.Delta_PRI_H5:
            return h5_controller.query_pvi_info(pvi_name,query_info)
        else:
            logger.error('unknow pvi type %s from name %s' % (pvi_type,pvi_name))
            
