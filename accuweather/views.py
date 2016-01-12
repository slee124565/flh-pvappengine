from django.shortcuts import render
from django.db.models import Max
from datetime import datetime, date, time, timedelta

from accuweather import *

import logging
logger = logging.getLogger(__name__)

# Create your views here.
from accuweather import CurrConditionType
from accuweather.models import CurrConditions

def get_current_conditions():
    '''
    return current condition information as dictionary object
    {
        CurrConditionType.Temperature : (value),
        CurrConditionType.UV_Index : (value),
        CurrConditionType.Visibility : (value),
    }
    '''
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
        
def query_daily_condition(condition=CurrConditionType.Temperature):
    '''
    return daily condition max value list object according to param condition type value
    [ [datetime,value],... ] 
    '''
    if condition == CurrConditionType.Temperature:
        col_name = 'temperature'
    elif condition == CurrConditionType.UV_Index:
        col_name = 'uv'
    elif condition == CurrConditionType.Visibility:
        col_name = 'visibility'
    
    queryset = CurrConditions.objects.values('prob_date'
                                        ).annotate(Max(col_name)
                                        ).order_by('-prob_date')
    info = []
    max_report_len = MAX_QUERY_CONDITION_DAILY_LIST_LEN # 45 days
    if queryset.count() < max_report_len:
        max_report_len = queryset.count()
    for entry in queryset[:max_report_len]:
        info.append([entry['prob_date'],entry[col_name+'__max']])
    logger.debug('query return:\n%s' % str(info))
    info.sort(key=lambda x: x[0])
    
    return info

def query_hourly_condition(condition=CurrConditionType.Temperature):
    '''
    return hourly condition max value list object according to param condition type value
    [ [datetime,value],... ] 
    '''
    if condition == CurrConditionType.Temperature:
        col_name = 'temperature'
    elif condition == CurrConditionType.UV_Index:
        col_name = 'uv'
    elif condition == CurrConditionType.Visibility:
        col_name = 'visibility'

    queryset = CurrConditions.objects.values( 'prob_date', 'prob_hour'
                            ).annotate(Max(col_name)
                            ).order_by('-prob_date','-prob_hour')
    logger.debug('sql cmd: %s' % str(queryset.query))
    info = []
    logger.debug('queryset count %d' % queryset.count())
    max_report_len = MAX_QUERY_CONDITION_HOURLY_LIST_LEN # last 48 hours
    if queryset.count() < max_report_len:
        max_report_len = queryset.count()
    for entry in queryset[:max_report_len]:
        t_hour = entry['prob_hour']
        t_time = time(t_hour,0,0)
        info.append([datetime.combine(entry['prob_date'],t_time),entry[col_name + '__max']])

    return info
    
    