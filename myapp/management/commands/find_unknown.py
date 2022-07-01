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
        tcs = TargetClassification.objects.all()
        total = len(tcs)
        unks = 0
        classifications = []
        counts = []
        for tc in tcs:
            if tc.classification == 'Unknown':
                unks +=1
            if not tc.source + ' ' + tc.classification in classifications:
                classifications.append(tc.source+ ' ' + tc.classification)
                counts.append(1)
            else:
                counts[classifications.index(tc.source+ ' ' + tc.classification)] +=1
            if tc.source + ' ' + tc.classification == 'ALeRCE Periodic':
                print(tc.target.name)
        print(f'{unks} out of {total} are unknown')
        for i in range(len(classifications)):
            print(classifications[i] + ' ' + str(counts[i]))