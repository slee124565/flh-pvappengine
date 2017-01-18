from django.db import models
#from django.utils import timezone
from datetime import datetime
from django.utils import timezone

def get_current_time_hour():
    return datetime.now().hour


# Create your models here.
class RegData(models.Model):
    modbus_id = models.IntegerField('modbus address',default=0)
    pvi_name = models.CharField('pvi name',max_length=20,default='')
    date = models.DateTimeField('log datetime',default=datetime.now)
    prob_date = models.DateField('log date',default=datetime.now)
    prob_time = models.TimeField('log time',default=datetime.now)
    prob_hour = models.IntegerField('hour of log time',default=get_current_time_hour)
    address = models.IntegerField('register address')
    value = models.IntegerField('register read value',default=0)
    sync_flag = models.BooleanField('sync flag with cloud',default=False)

    def save(self, *args, **kwargs):
        if self.date is None:
            self.date = datetime.now()
        self.prob_date = self.date.date()
        self.prob_time = self.date.time()
        self.prob_hour = self.date.hour
        super(RegData, self).save(*args, **kwargs)   
        
class EnergyData(models.Model):
    '''Energy Type Enum ['DAILY', 'MONTHLY', 'YEARLY']
    '''
    modbus_id = models.IntegerField('modbus address',default=0)
    date = models.DateField('energy date',default=timezone.now)
    type = models.CharField('energy type',max_length=20,default='')
    value = models.IntegerField('energy value',default=0)
    sync_flag = models.BooleanField('sync flag',default=False)

    