from django.shortcuts import render
from datetime import datetime, date, time, timedelta
import logging
logger = logging.getLogger(__name__)

# Create your views here.
from accuweather import CurrConditionType
from accuweather.models import CurrConditions

def get_current_conditions():
    time_since = (datetime.now() + timedelta(minutes=-30)).time()
    time_until = datetime.now().time()
    queryset = CurrConditions.objects.filter(prob_date__exact=datetime.now().date()
                                        ).filter(prob_date__exact=datetime.now().date()
                                        ).filter(prob_time__range=[time_since,time_until]
                                        ).order_by('-id')
    if len(queryset) > 0:
        info = {
                CurrConditionType.Temperature : queryset[0].temperature,
                CurrConditionType.UV_Index : queryset[0].uv,
                CurrConditionType.Visibility : queryset[0].visibility,
                }
        logger.debug('get_current_conditions: %s' % str(info))
    else:
        logger.error('no current conditions info return')
        info = {
                CurrConditionType.Temperature : 'N/A',
                CurrConditionType.UV_Index : 'N/A',
                CurrConditionType.Visibility : 'N/A',
                }
    return info
        
