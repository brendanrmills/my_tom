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
from urllib.parse import urlencode
LASAIR_URL = 'https://lasair-ztf.lsst.ac.uk/api'

class Command(BaseCommand):

    help = 'This command is built to tecover all the lost target classifications'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        num_tcs = []
        counts = []
        # for t in TargetList.objects.get(name='Alerce + Fink + Lasair').targets.all():
        #     l = len(t.targetclassification_set.all())
        #     if l in num_tcs:
        #         counts[num_tcs.index(l)] += 1
        #     else:
        #         num_tcs.append(l)
        #         counts.append(1)
        #     if l == 125:
        #         print(t.name)
        #         for tc in t.targetclassification_set.all():
        #             print(tc.as_dict())
        # for i in range(len(counts)):
        #     print(num_tcs[i] , counts[i])
        # self.recover_fink()
        # print('Done with Fink')
        self.recover_lasair()
        # print('done with Lasair')
        # self.recover_alerce()
        # self.recover_alerce2()
        # print('Done with Alerce')



        return 'Success!'
    
    def recover_fink(self):
        i = 0
        targets = TargetList.objects.get(name='Fink').targets.all()
        for target in targets:
            if not target.targetclassification_set.filter(source='Fink').exists():
                tes = target.targetextra_set.all()
                classif = tes.get(key='fink_v:classification').typed_value('')
                mjd = tes.get(key = 'fink_i:jd').typed_value('number') - 2400000

                save_target_classification(target, 'Fink', '', classif, 1.0, mjd)
                save_target_classification(target, 'Fink', '', 'fink_mulens', tes.get(key = 'fink_d:mulens').typed_value('number'), mjd)
                save_target_classification(target, 'Fink', '', 'fink_sso', tes.get(key = 'fink_d:roid').typed_value('number'), mjd)
                save_target_classification(target, 'Fink', '', 'fink_KN', tes.get(key = 'fink_d:rf_kn_vs_nonkn').typed_value('number'), mjd)
                save_target_classification(target, 'Fink', '', 'fink_SNIa', tes.get(key = 'fink_d:snn_snia_vs_nonia').typed_value('number'), mjd)
                i+=1
        print(i)
    
    def recover_alerce(self):
        i = 0
        targets = TargetList.objects.get(name='ALeRCE + Lasair').targets.all()
        for target in targets:
            if not target.targetclassification_set.filter(source='ALeRCE').exists():
                try:
                    url = 'https://api.alerce.online/ztf/v1/objects/'+target.name+'/probabilities'
                    response = requests.get(url)
                    response.raise_for_status()
                    probs = response.json()
                    alerce_probs(target, probs)
                    i+=1
                except:
                    pass
        print(i)

    def recover_alerce2(self):
        i = 0
        targets = TargetList.objects.get(name='ALeRCE + Fink').targets.all()
        for target in targets:
            if not target.targetclassification_set.filter(source='ALeRCE').exists():
                try:
                    url = 'https://api.alerce.online/ztf/v1/objects/'+target.name+'/probabilities'
                    response = requests.get(url)
                    response.raise_for_status()
                    probs = response.json()
                    alerce_probs(target, probs)
                    i+=1
                except:
                    pass
        print(i)

    def recover_lasair(self):
        i = 0
        lasair_broker = LasairBroker()
        targets = TargetList.objects.get(name='Lasair + Fink').targets.all()
        for target in targets:
            if not target.targetclassification_set.filter(source='Lasair').exists():
                try:
                    query = {
                        'selected': 'objects.objectId, objects.ramean, objects.decmean, objects.jdmax, sherlock_classifications.classification, sherlock_classifications.classificationReliability',
                        "token":"1ce34af3a313684e90eb86ccc22565ae33434e0f",
                        'tables': 'objects, sherlock_classifications',
                        'conditions': f'objects.objectId LIKE "{target.name}"',
                        'limit': 1,
                        'offset': 0,
                        'format': 'json',
                    }
                    url = LASAIR_URL + '/query/?' + urlencode(query)
                    response = requests.get(url)
                    response.raise_for_status()
                    parsed = response.json()[0]
                    save_target_classification(target, 'Lasair', '', parsed['classification'], parsed['classificationReliability'], parsed['jdmax']-2400000)
                    target.save(extras={'lasair_sherlock': parsed['classification']})
                    i+=1
                except Exception as e:
                    print(e)
                    pass

        print(i)
    def recover_lasair2(self):
        i = 0
        lasair_broker = LasairBroker()
        targets = TargetList.objects.get(name='ALeRCE + Lasair').targets.all()
        for target in targets:
            if not target.targetclassification_set.filter(source='Lasair').exists():
                try:
                    query = {
                        'selected': 'objects.objectId, objects.ramean, objects.decmean, objects.jdmax, sherlock_classifications.classification, sherlock_classifications.classificationReliability',
                        "token":"1ce34af3a313684e90eb86ccc22565ae33434e0f",
                        'tables': 'objects, sherlock_classifications',
                        'conditions': f'objects.objectId LIKE "{target.name}"',
                        'limit': 1,
                        'offset': 0,
                        'format': 'json',
                    }
                    url = LASAIR_URL + '/query/?' + urlencode(query)
                    response = requests.get(url)
                    response.raise_for_status()
                    parsed = response.json()[0]
                    save_target_classification(target, 'Lasair', '', parsed['classification'], parsed['classificationReliability'], parsed['jdmax']-2400000)
                    target.save(extras={'lasair_sherlock': parsed['classification']})
                    i+=1
                except Exception as e:
                    print(e)
                    pass

        print(i)

