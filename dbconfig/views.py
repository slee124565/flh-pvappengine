from django.shortcuts import render

from dbconfig.models import AppOption

import logging, json

logger = logging.getLogger(__name__)

def get_app_json_db_config(app_name, default_json):
    entry, created = AppOption.objects.get_or_create(app_name = app_name)
    if created:
        logger.info('create new entry for app name %s and default json saved' % app_name)
        entry.json_data = json.dumps(default_json)
        entry.save()
    
    return json.loads(entry.json_data)

# Create your views here.
