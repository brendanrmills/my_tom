from django.core.management.base import BaseCommand
from tom_targets.models import Target, TargetList
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker
from tom_alerts.brokers.alerce import ALeRCEBroker
from tom_fink.fink import FinkBroker
from merge_methods import *
import time, json, logging, requests
from astropy.time import Time
from classifications.models import TargetClassification
from dateutil.parser import parse
from urllib.parse import urlencode

class Command(BaseCommand):

    help = 'This is a playground function so I can quickly test things out'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        mjd__gt = 59087 #minimum date
        mjd__lt = 59088 #maximum date

        today = 2459765
        yesterday = 2459764
        
        # alerts = self.get_lasair(yesterday, today)
        # merge_lasair(alerts)

        LASAIR_URL = 'https://lasair-ztf.lsst.ac.uk/api'
        query = {
            'limit': 1,
            "token":"1ce34af3a313684e90eb86ccc22565ae33434e0f",
            'objectIds': 'ZTF19aaxkgrl',
            'format': 'json',
            
        }
        url = LASAIR_URL + '/objects/?' + urlencode(query)
        print(url)
        response = requests.get(url)
        response.raise_for_status()
        parsed = response.json()
        print(json.dumps(parsed, indent = 3))

        return 'Success!'

    def get_lasair(self, mjd__gt, mjd__lt):
        start_time = time.time()
        LASAIR_URL = 'https://lasair-ztf.lsst.ac.uk/api'
        query = {
            'selected': 'objects.objectId, objects.ramean, objects.decmean, objects.jdmax, sherlock_classifications.classification, sherlock_classifications.classificationReliability',
            "token":"1ce34af3a313684e90eb86ccc22565ae33434e0f",
            'tables': 'objects, sherlock_classifications',
            'conditions': f'objects.jdmax>{mjd__gt} AND objects.jdmax<{mjd__lt}',
            'limit': 5000,
            'offset': 0,
            'format': 'json',
        }
        url = LASAIR_URL + '/query/?' + urlencode(query)
        print(url)
        response = requests.get(url)
        response.raise_for_status()
        parsed = response.json()
        lasair_alert_list = list(parsed)

        logging.info('Lasair took {} sec to gather {} alerts'.format(time.time() - start_time, len(lasair_alert_list)))
        return lasair_alert_list