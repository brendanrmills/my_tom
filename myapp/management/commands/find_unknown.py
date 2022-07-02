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
import numpy as np

class Command(BaseCommand):

    help = 'This is a playground function so I can quickly test things out'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        # targets = list(Target.objects.all())
        # print(len(targets), ' targets')
        # tcs = TargetClassification.objects.all()
        # no_classif = 0
        # unks = 0
        # for t in targets:
        #     tcs = t.targetclassification_set.all()
        #     if len(tcs) == 0:
        #         no_classif += 1
        #     if len(tcs) == 1 and tcs[0].classification == 'Unknown':
        #         unks += 1
        #     if len(tcs) > 2:
        #         print(t.name, t.targetextra_set.get(key = 'broker'))

        # print(no_classif, ' have no classification')
        # print(unks, ' are unknown')
        
        # t = Target.objects.get(name = 'ZTF18abmahnn')
        # print(TargetClassification.objects.filter(target = t))
        t = Target.objects.get(name = 'ZTF20abvvvze')
        tcs = TargetClassification.objects.filter(target = t)
        for tc in tcs:
            print(tc)

        # total = len(tcs)
        # unks = 0
        # classifications = []
        # counts = []
        # for tc in tcs:
        #     if tc.classification == 'Unknown':
        #         unks +=1
        #     if not tc.source + ' ' + tc.classification in classifications:
        #         classifications.append(tc.source+ ' ' + tc.classification)
        #         counts.append(1)
        #     else:
        #         counts[classifications.index(tc.source+ ' ' + tc.classification)] +=1
        #     if tc.source + ' ' + tc.classification == 'ALeRCE Periodic':
        #         print(tc.target.name)
        # print(f'{unks} out of {total} are unknown')
        # for i in range(len(classifications)):
        #     print(classifications[i] + ' ' + str(counts[i]))
    def clean_duplicate_classifs(self):
        targets = list(Target.objects.all())
        dups = 0
        for t in targets:
            tcs = TargetClassification.objects.filter(target = t)
            tc_dicts = [tc.as_dict() for tc in tcs]
            for tc in tcs:
                if tc_dicts.count(tc.as_dict()) > 1:
                    print('I found a duplicate classification', tc)
                    dups += 1
                    tc.delete()
                    tcs = TargetClassification.objects.filter(target = t)
                    tc_dicts = [tc.as_dict() for tc in tcs]
        return dups


    def count_tcs(self):
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
        