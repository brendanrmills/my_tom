from django.core.management.base import BaseCommand
from tom_targets.models import Target, TargetList
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker
from tom_alerts.brokers.alerce import ALeRCEBroker
from tom_fink.fink import FinkBroker
from tom_alerts.brokers.lasair import LasairBroker
from merge_methods import *
import time, json, logging, requests
from astropy.time import Time
from tom_classifications.models import TargetClassification
from dateutil.parser import parse
from urllib.parse import urlencode
from plotly import offline
from plotly.subplots import make_subplots
from plotly import graph_objs as go

class Command(BaseCommand):

    help = 'This is a playground function so I can quickly test things out'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        mjd__gt = 59087 #minimum date
        mjd__lt = 59088 #maximum date

        today = 59765
        yesterday = 59764
        targets = TargetList.objects.get(name='Alerce + Fink + Lasair').targets.all()
        # i=0
        # j = 0
        # for t in targets:
        #     if len(t.targetclassification_set.all()) > 10:
        #         i+=1
        #     if len(t.targetclassification_set.all()) > 12:
        #         j+=1
        # print(i,j)

        register_lists()
        # targets = TargetList.objects.get(name='Alerce + Fink + Lasair').targets.all()
        # i = 0
        # for t in targets:
        #     if len(t.targetclassification_set.all()) >8 and i<20:
        #         print(t.name)
        #         i+=1

        # # get the probabilities
        # url = 'https://api.alerce.online/ztf/v1/objects/'+t.name+'/probabilities'
        # response = requests.get(url)
        # response.raise_for_status()
        # probs = response.json()
        # logging.info(t.name)
        # alerce_probs(t, probs)
        # print(probs)
 


        return 'Success!'


    def get_fink(self, mjd__gt, mjd__lt):
        st = time.time()
        fink_broker = FinkBroker()
        fink_alert_list_big = []

        dur = mjd__lt-mjd__gt
        offset = 0
        i = 0
        while offset < dur:# and len(fink_alert_list_big) < 50: #this line keeps fink from running all 25000, comment out before and
            t = Time(mjd__gt + offset,format = 'mjd')
            window = 3
            if offset + window/24 > dur:
                window = dur - offset
            query = {
                'objectId': '', 
                'conesearch': '', 
                'datesearch': f'{t.iso}, {window*60}',
                'classsearch': '', 
                'classsearchdate': '', 
                'ssosearch': ''
            }
            offset += 3/24

            fink_alerts = fink_broker.fetch_alerts(query)

            fink_alert_list = list(fink_alerts)
            for a in fink_alert_list:
                fink_alert_list_big.append(a)
            i+=1

        logging.info(f'Fink took {time.time() - st } sec to gather {len(fink_alert_list_big)} alerts')
        return fink_alert_list_big
