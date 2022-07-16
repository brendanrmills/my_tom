from django.core.management.base import BaseCommand
from tom_targets.models import Target, TargetList
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker
from tom_alerts.brokers.alerce import ALeRCEBroker
from tom_fink.fink import FinkBroker
from merge_methods import *
import time, json, logging, requests
from astropy.time import Time
from tom_classifications.models import TargetClassification
import numpy as np

class Command(BaseCommand):

    help = 'This is a playground function so I can quickly test things out'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        FORMAT = '%(asctime)s %(message)s'
        logging.basicConfig(format = FORMAT, filename='/home/bmills/bmillsWork/tom_test/mytom/find_unknown.log', level=logging.INFO, force=True)
        
        # register_duplicates()
        # clean_duplicate_classifs()
        # find_unknowns()
        # t = Target.objects.get(name='ZTF20abncmfk')
        # tcs = t.targetclassification_set.all()
        # for tc in tcs:
        #     print(tc.as_dict())
        self.classification_printout()
        # for t in TargetList.objects.get(name='ALeRCE').targets.all():
        #     # get the probabilities
        #     url = 'https://api.alerce.online/ztf/v1/objects/'+t.name+'/probabilities'
        #     response = requests.get(url)
        #     response.raise_for_status()
        #     probs = response.json()
        #     logging.info(t.name)
        #     alerce_probs(t, probs)
        # logging.info('Done')

    def count_tcs(self):
        '''This method goes though all the targets and sees hoe many target classifications it has
        It prints out a list showing how many classifications a target might have, and how many 
        targets have that may classifications. '''
        targets = list(Target.objects.all())
        lengths = []
        counts = []
        names = []
        for t in targets:
            tcs = TargetClassification.objects.filter(target = t)
            l = len(tcs)
            try:
                i = lengths.index(l)
                counts[i] += 1
                names[i].append(t.name)
            except:
                lengths.append(l)
                counts.append(1)
                names.append([t.name])

        
        order = np.argsort(lengths)
        for i in order:
            print(lengths[i], counts[i])

        print(names[-1][0])
        return lengths, counts, names
    
    def classification_printout(self):
        tcs = TargetClassification.objects.all()
        total = len(tcs)
        classifications = []
        counts = []
        for tc in tcs:
            text = tc.source + ' ' + tc.classification
            if not text in classifications:
                classifications.append(text)
                counts.append(1)
            else:
                counts[classifications.index(text)] +=1
        for i in range(len(classifications)):
            print("'" + classifications[i] + "': " +  "'" + str(counts[i]) + "'")
        print(len(classifications))
        print(f'there are {total} total classifications')