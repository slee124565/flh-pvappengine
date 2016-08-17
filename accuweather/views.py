from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Max
from datetime import datetime, date, time, timedelta

#from accuweather import *
from dbconfig.views import get_app_json_db_config

import urllib.request, json
import logging
import accuweather
logger = logging.getLogger(__name__)

# Create your views here.
from accuweather import *
from accuweather.models import CurrConditions

def clear_expired_records():
    expired_date = date(date.today().year-1,1,1)
    count, _ = CurrConditions.objects.filter(prob_date__lt = expired_date).delete()
    if count > 0:
        logger.info('clear expired records %d' % count)
    else:
        logger.debug('no expired %s records' % str(expired_date))
    
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
    
    date_since = (datetime.now() + timedelta(days=-MAX_QUERY_CONDITION_DAILY_LIST_LEN)).date()
    queryset = CurrConditions.objects.values('prob_date'
                                        ).filter(prob_date__gt=date_since
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

    date_since = (datetime.now() + timedelta(hours=-MAX_QUERY_CONDITION_HOURLY_LIST_LEN)).date()

    queryset = CurrConditions.objects.values( 'prob_date', 'prob_hour'
                            ).filter(prob_date__gt=date_since
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

def aw_search_location_by_geo(latitude,longitude):
    '''
    AccuWeather search location by GeoPosition API
    return json data
    '''
    info = {}
    dbconfig = get_app_json_db_config('accuweather', accuweather.DEFAULT_DB_CONFIG)
    t_apikey = dbconfig['apikey']
    t_url = AccuWeather_Location_Geo_Search_API.format(latitude=latitude,
                                                       longitude=longitude,
                                                       apikey=t_apikey)
    try:
        logger.debug(t_url)
        with urllib.request.urlopen(t_url) as http_resp:
            info = json.loads(http_resp.read().decode('utf-8'))
            logger.debug(str(info))
    except:
        logger.error('aw_search_location_by_geo error', exc_info=True)
    return info

def aw_locations_api(location_key):
    '''
    AccuWeather Location API
    return json data
    '''
    info = {}
    dbconfig = get_app_json_db_config('accuweather', accuweather.DEFAULT_DB_CONFIG)
    t_apikey = dbconfig['apikey']
    t_url = AccuWeather_Location_API.format(locationkey=location_key,
                                            apikey=t_apikey)
    try:
        logger.debug(t_url)
        with urllib.request.urlopen(t_url) as http_resp:
            info = json.loads(http_resp.read().decode('utf-8'))
            logger.debug(str(info))
    except:
        logger.error('aw_locations_api error', exc_info=True)
    return info
    
    
def accuweather_geo_location_search(request):
    '''
    web api for querying location by GeoPosition
    param name: q
    url example: http://hostname:port/path/?q=latitude,longitude
    '''
    try:
        latitude,longitude = request.GET.get('q').split(',')
        resp = HttpResponse(content_type='text/plain')
        resp.content = json.dumps( aw_search_location_by_geo(latitude,longitude),indent=4)
        return resp
    except:
        logger.warning('accuweather_geo_location_search error', exc_info=True)
        return HttpResponse('{}')
    
def accuweather_location_key_geo_search(request):
    '''
    web api for query location key by GeoPosition directly
    param name: q
    url example: http://hostname:port/path/?q=latitude,longitude    
    '''
    try:
        latitude,longitude = request.GET.get('q').split(',')
        resp = HttpResponse(content_type='text/plain')
        location_key = aw_search_location_by_geo(latitude,longitude).get('Key')
        location_data = aw_locations_api(location_key)
        resp.content = 'AccuWeather Location Key: ' + location_key + '\n' + \
                        'LocalizedName: ' + location_data['LocalizedName'] + ' ' + \
                        location_data.get('SupplementalAdminAreas')[0].get('LocalizedName') + ' ' + \
                        location_data['AdministrativeArea']['LocalizedName'] + ' ' + \
                        location_data['Country']['LocalizedName'] + \
                        '\n' + json.dumps(location_data, ensure_ascii=False, indent=4) 
        return resp
    except:
        logger.warning('accuweather_location_key_geo_search error', exc_info=True)
        resp.content = json.dumps(location_data, ensure_ascii=False, indent=4)
        return resp
    