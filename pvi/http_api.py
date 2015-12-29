from django.http import HttpResponse
from pvi.models import RegData
from pvi.h5 import controller as pvi_h5

INFO_KEY_ENERGY = 'energy'
PVI_TYPE_DELTA_PRI_H5 = 'DELTA_PRI_H5'

def get_pvi_type_by_name(pvi_name):
    if pvi_name in ['H5']:
        return PVI_TYPE_DELTA_PRI_H5
    else:
        return None
    
def query(request,pvi_name,period_type,info_name):
    if info_name == INFO_KEY_ENERGY:
        if period_type in ['hourly','daily']:
            if get_pvi_type_by_name(pvi_name) == PVI_TYPE_DELTA_PRI_H5:
                return HttpResponse(pvi_h5.get_pvi_energy_info_json(period_type))
            else:
                return HttpResponse('ValueType Error PVI Name %s Error' % pvi_name)
        else:
            return HttpResponse('ValueType Error Period Type %s Error' % period_type)
    else:
        return HttpResponse('ValueType Error Information Name %s Error' % info_name)
        
    
