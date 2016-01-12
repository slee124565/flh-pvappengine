
API_KEY = 'ff1b463d98fb47af848ea2843ec5c925'
LocationKey_Taipei = '3-315078_1_AL'
AccuWeather_API = 'http://api.accuweather.com/currentconditions/v1/{locationKey}.json?apikey={apikey}&language=zh-tw&details=true'

MAX_QUERY_CONDITION_DAILY_LIST_LEN = 45
MAX_QUERY_CONDITION_HOURLY_LIST_LEN = 48

from enum import Enum

class CurrConditionType:
    Temperature = 1
    UV_Index = 2
    Visibility = 3