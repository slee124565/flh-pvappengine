

AccuWeather_API = 'http://api.accuweather.com/currentconditions/v1/{locationKey}.json?\
apikey={apikey}&language=zh-tw&details=true&getphotos=false'

AccuWeather_Location_Geo_Search_API = 'http://api.accuweather.com/locations/v1/cities/geoposition/search.json?\
q={latitude},{longitude}&apikey={apikey}&language=zh-tw&details=true&toplevel=false'

AccuWeather_Location_API = 'http://api.accuweather.com/locations/v1/{locationkey}.json?\
apikey={apikey}&language=zh-tw&details=true'

MAX_QUERY_CONDITION_DAILY_LIST_LEN = 45
MAX_QUERY_CONDITION_HOURLY_LIST_LEN = 48

from enum import Enum

class CurrConditionType:
    Temperature = 1
    UV_Index = 2
    Visibility = 3
    
DEFAULT_DB_CONFIG = {
                      'apikey': 'ff1b463d98fb47af848ea2843ec5c925',
                      #-> get location key by geo 
                      #-> http://127.0.0.1:8000/appeng/accu/key_geo_search/?q=25.1058006,121.5198715
                      'locationkey': '2516626', 
                      #'locationkey': '701769', #-> Taipei
                     }
    