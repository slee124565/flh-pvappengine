from django.db import models

# Create your models here.
class RegData(models.Model):
    modbus_id = models.IntegerField('modbus address',default=0)
    pvi_name = models.CharField('pvi name',max_length=20,default='')
    date = models.DateTimeField('log datetime')
    address = models.IntegerField('register address')
    value = models.IntegerField('register read value',default=0)
    sync_flag = models.BooleanField('sync flag with cloud',default=False)
    