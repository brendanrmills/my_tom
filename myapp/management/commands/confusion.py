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
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

class Command(BaseCommand):

    def handle(self, *args, **options):
        alst_codes = {#these dictionaries set ip the conversion between what the crokers call their classifications and the SIMBAD codes
            'SN': 'SN*',
            'AGN': 'AGN',
            'VS': 'V*',
            'bogus': 'err',
            'asteroid': 'ast',
        }
        las_codes = {#still need to handle bright star
            'VS': 'V*',
            'CV': 'CV*',
            'SN': 'SN*',
            'ORPHAN': '?',
            'AGN': 'AGN',
            'NT': 'Transient',
            'UNCLEAR': '?',
            # 'BS':
        }
        fink_codes = {
            'Tracklet': 'trk',
            'Solar System MPC': 'MPC',
            'Solar System candidate': 'SSO',
            'SN candidate': 'SN*',
            'Early SN Ia candidate': 'SNIa',
            'Microlensing candidate': 'Lev',
            'Kilonova candidate': 'KN',
            'fink_mulens': 'Lev',
            'fink_sso': 'SSO',
            'fink_KN': 'KN',
            'fink_SNIa': 'SNIa',
        }
        with open('/home/bmills/bmillsWork/tom_test/mytom/SIMBAD_otypes_labels.txt') as f:#this uses a file downloaded for simbad to deal with old codes
            for line in f:
                [_, code, old, new] = line.split('|')
                fink_codes[old.strip()] = code.strip()
                fink_codes[new.strip()] = code.strip()
        with open('/home/bmills/bmillsWork/tom_test/mytom/variability.txt') as json_file:#this loads the parentage dictionary that I made
            parents_dict = json.load(json_file)
        targets = TargetList.objects.get(name='Alerce + Fink + Lasair').targets.all()
        cap = 0
        sources = ['ALeRCE Stamp', 'Lasair', 'Fink']#this is the order that the choices are arranged, make sure this is consistent with the assignment below
        big_choices = [[], [], []]
        for t in targets:
            tcs = t.targetclassification_set.all()#looks at all the associated target classifications and assesses the how many there are
            if cap < 5000:
                #these lines pick the classification with the highest probability form each broker
                try:
                    stamp_choice = alst_codes[tcs.filter(level='stamp_classifier_1.0.4').order_by('mjd', '-probability')[0].classification]
                    stamp_choice = alst_codes[tcs.filter(level='stamp_classifier_1.0.4').order_by('mjd', '-probability')[0].classification]
                    las_choice = las_codes[tcs.filter(source='Lasair').order_by('mjd', '-probability')[0].classification]
                    fink_choice = fink_codes[tcs.filter(source='Fink').order_by('mjd', '-probability')[0].classification]
                    catch_list = ['SN*', 'CV*', 'AGN', 'V*', 'Other', 'Alert']
                    choices = [stamp_choice, las_choice, fink_choice]
                    
                    for i in range(len(choices)):
                        while not choices[i] in catch_list:
                            choices[i] = parents_dict[choices[i]]
                        big_choices[i].append(choices[i])
                    cap += 1
                except:
                    pass

        
        cm = confusion_matrix(big_choices[1], big_choices[2], labels=catch_list)
        print(cm)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=catch_list)
        disp.plot()
        plt.show()
        return 'Success!'