from django.core.management.base import BaseCommand
from tom_targets.models import Target, TargetClassification
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker
from tom_alerts.brokers.alerce import ALeRCEBroker
from tom_fink.fink import FinkBroker
from merge_methods import *
import time, json, logging, requests
from astropy.time import Time

class Command(BaseCommand):

    help = 'This command calls two brokers, gets the alerts for a day and merges the alerts via Targets and TargetExtras'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):


        target = Target.objects.get(name = 'ZTF18abfhxsa')
        target.save(extras = {'test': 50})
        print(target.targetextra_set.get(key = 'test'))

        sample_classif = {
            'broker': 'test',
            'type': 'star',
            'prob': 0.75,
            'mjd':50000
        }
        target.save(classification = sample_classif)

        c = TargetClassification.objects.get(target = target.id)
        print(c)

        c = target.targetclassification_set.all()
        print(c)
        print(c[0].as_dict())

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