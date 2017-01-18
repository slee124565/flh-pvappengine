from django.test import TestCase

from .views import do_action_on_pvs, action_load_pvi_eng_history
from dbconfig.views import get_app_json_db_config
import pvi


# Create your tests here.
class PviTestCase(TestCase):
    
    def test_do_action_on_pvs_load_eng_history(self):
        do_action_on_pvs(
            get_app_json_db_config('pvi', pvi.DEFAULT_DB_CONFIG),
            action_load_pvi_eng_history)
    