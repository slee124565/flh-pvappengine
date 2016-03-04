from django.db import models

# Create your models here.
class AppOption(models.Model):
    """
    access database table with columns: app_name & json_data.
    app_name is django app name, and 
    json_data is django app options in json format
    """
    app_name = models.CharField('App Name Index Key', max_length=20, null = False)
    json_data = models.TextField('App Option Json Data', default = '')