

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