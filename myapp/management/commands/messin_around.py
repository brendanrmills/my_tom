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

class Command(BaseCommand):

    help = 'This is a playground function so I can quickly test things out'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        mjd__gt = 59087 #minimum date
        mjd__lt = 59088 #maximum date

        target = Target.objects.get(name = 'ZTF20abwyboe')
        tc = TargetClassification.objects.get(target = target)
        print(tc)
        tc = target.targetclassification_set.all()
        print(tc)

        


        # dups = TargetList.objects.create(name = 'Duplicates')
        # trips = TargetList.objects.create(name = 'Triplicates')
        # targets_all = Target.objects.all()
        # for t in targets_all:
        #     broker_list = t.targetextra_set.get(key = 'broker').typed_value('').split(', ')
        #     if 'MARS' in broker_list:
        #         mars_tg.targets.add(t)
        #     if 'ANTARES' in broker_list:
        #         antares_tg.targets.add(t)
        #     if 'Fink' in broker_list:
        #         fink_tg.targets.add(t)
        #     if 'ALeRCE' in broker_list:
        #         alerce_tg.targets.add(t)
        #     if len(broker_list) == 2:
        #         dups.targets.add(t)
        #     if len(broker_list) == 3:
        #         trips.targets.add(t)
        
        # print(mars_tg.targets.all())

        
        # print(tg)
        # for target in Target.objects.all():
        #     # if target in tg.targets.all():
        #     #     continue
        #     brokers = target.targetextra_set.get(key = 'broker').typed_value('').split(', ')
        #     print(brokers)
        #     if 'MARS' in brokers:
        #         tg.targets.add(target)
        #         print('Added to MARS')
        # for t in tg.targets.all():
        #     print(t)


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

        # get the probabilities
        # url = 'https://api.alerce.online/ztf/v1/objects/ZTF17aacmiuz/probabilities'
        # target = Target.objects.get_or_create(name = 'ZTF17aacmiuz')
        # response = requests.get(url)
        # response.raise_for_status()
        # probs = response.json()
        # print(json.dumps(probs, indent = 3))
        # mjd = target.targetextra_set.get(key = 'alerce_lastmjd').typed_value('number')
        # if probs:
        #     for p in probs:
        #         if p['classifier_version'] =="stamp_classifier_1.0.4":
        #             save_target_classification(target, 'ALeRCE*', p['classifier_name'] + '*', p['class_name'] + '*', p['probability'], mjd)
        #         else:
        #             save_target_classification(target, 'ALeRCE', p['classifier_name'], p['class_name'], p['probability'], mjd)
        # else:
        #     save_target_classification(target, 'ALeRCE', '', 'Unknown', 0.0, mjd)

        # target.save(extras = alerce_properties)
        # save_broker_extra(target, 'ALeRCE')
        # print('ALeRCE  Target', alert["oid"], ' created'if created else ' updated!!!')
        # print(time.time() - st)


        return 'Success!'