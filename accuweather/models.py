from django.db import models
from datetime import datetime
from accuweather import *
import urllib.request, json, logging

logger = logging.getLogger(__name__)

current_location_key = LocationKey_Taipei

class CurrConditions(models.Model):
    prob_date = models.DateField(default=datetime.now)
    prob_time = models.TimeField(default=datetime.now)
    prob_hour = models.IntegerField()
    temperature = models.FloatField(default=0.0)
    uv = models.IntegerField(default=0)
    visibility = models.FloatField(default=0.0)
    sync_flag = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.prob_hour = self.prob_time.hour
        super(CurrConditions, self).save(*args, **kwargs)   

    def __str__(self):
        return ','.join([str(self.prob_date),
                         str(self.prob_time),
                         str(self.prob_hour),
                         str(self.temperature),
                         str(self.uv),
                         str(self.visibility),
                         str(self.sync_flag)])
    
    @classmethod
    def save_current_location_condition(cls):
        api_uri = AccuWeather_API.format(locationKey=current_location_key,
                                         apikey=API_KEY)
        logger.debug('api_url: ' + api_uri)
        with urllib.request.urlopen(api_uri) as http_resp:
            curr_weather = json.loads(http_resp.read().decode('utf-8'))
            db_entry = CurrConditions(
                                   temperature = float(curr_weather[0]['ApparentTemperature']['Metric']['Value']),
                                   uv = int(curr_weather[0]['UVIndex']),
                                   visibility = float(curr_weather[0]['Visibility']['Metric']['Value'])
                                   )
            db_entry.save()
            logger.info('save pvstion current condition: %s' % str(db_entry) )
            