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
    def save_current_location_condition(cls, location_key):
        '''
        fetch location weather information from AccuWeather web server
        and save into database
        '''
        api_uri = AccuWeather_API.format(locationKey = location_key,
                                         apikey = API_KEY)
        logger.debug('api_url: ' + api_uri)
        try:
            with urllib.request.urlopen(api_uri) as http_resp:
                curr_weather = json.loads(http_resp.read().decode('utf-8'))
                t_temperature = curr_weather[0]['ApparentTemperature']['Metric']['Value']
                t_uv = curr_weather[0]['UVIndex']
                t_visibility = curr_weather[0]['Visibility']['Metric']['Value']
                db_entry = CurrConditions(
                                          prob_hour = datetime.now().hour,
                                          temperature = float(t_temperature),
                                          uv = int(t_uv),
                                          visibility = float(t_visibility)
                                          )
                logger.debug('current condition: %s, %s, %s' % (t_temperature,t_uv,t_visibility))
                db_entry.save()
                logger.info('save pvstion current condition: %s' % str(db_entry) )
        except Exception as e:
            logger.error('save_current_location_condition error', exc_info=True)
            