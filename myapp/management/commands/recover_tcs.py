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

class Command(BaseCommand):

    help = 'This command is built to tecover all the lost target classifications'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        # self.recover_fink()
        # print('Done with Fink')
        # self.recover_alerce()
        # print('Done with Alerce')
        self.recover_lasair()

        return 'Success!'
    
    def recover_fink(self):
        targets = TargetList.objects.get(name='Fink').targets.all()
        for target in targets:
            tes = target.targetextra_set.all()
            classif = tes.get(key='fink_v:classification').typed_value('')
            mjd = tes.get(key = 'fink_i:jd').typed_value('number') - 2400000

            save_target_classification(target, 'Fink', '', classif, 1.0, mjd)
            save_target_classification(target, 'Fink', '', 'fink_mulens', tes.get(key = 'fink_d:mulens').typed_value('number'), mjd)
            save_target_classification(target, 'Fink', '', 'fink_sso', tes.get(key = 'fink_d:roid').typed_value('number'), mjd)
            save_target_classification(target, 'Fink', '', 'fink_KN', tes.get(key = 'fink_d:rf_kn_vs_nonkn').typed_value('number'), mjd)
            save_target_classification(target, 'Fink', '', 'fink_SNIa', tes.get(key = 'fink_d:snn_snia_vs_nonia').typed_value('number'), mjd)
    
    def recover_alerce(self):
        targets = TargetList.objects.get(name='ALeRCE').targets.all()
        for target in targets:
            url = 'https://api.alerce.online/ztf/v1/objects/'+target.name+'/probabilities'
            response = requests.get(url)
            response.raise_for_status()
            probs = response.json()
            alerce_probs(target, probs)
    
    def recover_lasair(self):
        targets = TargetList.objects.get(name='Lasair').targets.all()
        lasair_broker = LasairBroker()
        for target in targets:
            classif = lasair_broker.fetch_alerts({'objectId': target.name})[0]['sherlock']['classification']
            classifRel = lasair_broker.fetch_alerts({'objectId': target.name})[0]['sherlock']['classificationReliability']
            mjd = lasair_broker.fetch_alerts({'objectId': target.name})[0]['candidates'][0]['mjd']
            save_target_classification(target, 'Lasair', '', classif, classifRel, mjd)
            target.save(extras={'lasair_sherlock': classif})

