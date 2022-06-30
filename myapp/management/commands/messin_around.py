from django.core.management.base import BaseCommand
from tom_targets.models import Target
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker
from tom_alerts.brokers.alerce import ALeRCEBroker
from tom_fink.fink import FinkBroker
from merge_methods import *
import time, json, logging, requests
from astropy.time import Time
from classifications.models import TargetClassification

class Command(BaseCommand):

    help = 'This is a playground function so I can quickly test things out'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        mjd__gt = 59087 #minimum date
        mjd__lt = 59088 #maximum date
        
        tcs = TargetClassification.objects.all()
        for tc in tcs:
            print(tc.as_dict())



        # alerce_broker = ALeRCEBroker()
        # query = {
        #     'stamp_classifier': '',
        #     'lc_classifier': '',
        #     'ra': '',
        #     'dec': '',
        #     'radius': '',
        #     'lastmjd__gt': mjd__gt,
        #     'lastmjd__lt': mjd__lt,
        #     'max_pages':1 #this line supresses a longer output
        # }
        # alerce_alerts = alerce_broker.fetch_alerts(query)
        # alerce_alert_list = list(alerce_alerts)[5:6]

        # merge_alerce(alerce_alert_list)

        # st = time.time()
        # try: #create target
        #     created = False
        #     target = Target.objects.get(name = alert["oid"])
        # except:
        #     target = ALeRCEBroker().to_target(alert)
        #     created = True
        # #redefines the keys of the alert to be preceded by "antares_"
        # alerce_properties = {}
        # for k in alert.keys():
        #     alerce_properties['alerce_{}'.format(k)] = alert[k]

        # # get the probabilities
        # url = 'https://api.alerce.online/ztf/v1/objects/'+alert['oid']+'/probabilities'
        # response = requests.get(url)
        # response.raise_for_status()
        # probs = response.json()
        # for i in range(len(probs)):
        #     target.save(extras = {'alerce_classification'+str(i): probs[i]})

        # target.save(extras = alerce_properties)
        # save_broker_extra(target, 'ALeRCE')
        # print('ALeRCE  Target', alert["oid"], ' created'if created else ' updated!!!')
        # print(time.time() - st)


        return 'Success!'