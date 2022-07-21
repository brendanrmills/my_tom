from locale import normalize
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
import pandas as pd
import numpy as np

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.alerce_codes = {#these dictionaries set ip the conversion between what the crokers call their classifications and the SIMBAD codes
            'SN': 'SN*',
            'AGN': 'AGN',
            'VS': 'V*',
            'bogus': 'err',
            'asteroid': 'ast',
        }
        self.allc_codes = {
            'SNIa': 'SNIa',
            'SNIbc': 'SNIbc',
            'SNII': 'SNII',
            'SLSN': 'SLSN',
            'QSO': 'QSO',
            'AGN': 'AGN',
            'Blazar': 'Bla',
            'CV/Nova': 'CV*',
            'YSO': 'Y*O',
            'LPV': 'LP*',
            'E': 'EB*',
            'DSCT': 'dS*',
            'RRL': 'RR*',
            'CEP': 'Ce*',
            'Periodic-Other': 'Pu*',
        }
        self.alerce_codes.update(self.allc_codes)
        self.las_codes = {#still need to handle bright star
            'VS': 'V*',
            'CV': 'CV*',
            'SN': 'SN*',
            'ORPHAN': '?',
            'AGN': 'AGN',
            'NT': 'Transient',
            'UNCLEAR': '?',
            # 'BS':
        }
        self.fink_codes = {
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
            'MIR': 'MIR',
            'NIR': 'NIR',
        }
        with open('/home/bmills/bmillsWork/tom_test/mytom/SIMBAD_otypes_labels.txt') as f:#this uses a file downloaded for simbad to deal with old codes
            for line in f:
                [_, code, old, new] = line.split('|')
                self.fink_codes[old.strip()] = code.strip()
                self.fink_codes[new.strip()] = code.strip()
        with open('/home/bmills/bmillsWork/tom_test/mytom/variability.txt') as json_file:#this loads the parentage dictionary that I made
            self.parents_dict = json.load(json_file)
        
        self.large_con()
        return 'Success!'
    
    def small_con(self):
        targets = TargetList.objects.get(name='Alerce + Fink + Lasair').targets.all()
        cap = 0
        j=0
        sources = ['ALeRCE Stamp', 'Lasair', 'Fink']#this is the order that the choices are arranged, make sure this is consistent with the assignment below
        big_choices = [[], [], []]
        for t in targets:
            tcs = t.targetclassification_set.all()#looks at all the associated target classifications and assesses the how many there are
            if cap < 5000:
                #these lines pick the classification with the highest probability form each broker
                stamp_set = tcs.filter(level='lc_classifier').order_by('mjd', '-probability')
                if not stamp_set.exists():
                    stamp_set = tcs.filter(level='stamp_classifier_1.0.4').order_by('mjd', '-probability')
                if not stamp_set.exists():
                    stamp_set = tcs.filter(level='stamp_classifier_1.0.0').order_by('mjd', '-probability')
                if not stamp_set.exists():
                    j += 1
                    continue
                stamp_tc = stamp_set[0]
                # print(stamp_tc.as_dict())
                stamp_choice = self.alerce_codes[stamp_tc.classification]
                try:
                    las_choice = self.las_codes[tcs.filter(source='Lasair').order_by('mjd', '-probability')[0].classification]
                except:
                    j+=1
                    continue
                fink_choice = self.fink_codes[tcs.filter(source='Fink').order_by('mjd', '-probability')[0].classification]
                if fink_choice == '?':
                    continue
                catch_list = ['SN*', 'CV*', 'AGN', 'V*', 'Alert']
                choices = [stamp_choice, las_choice, fink_choice]
                
                for i in range(len(choices)):
                    while not choices[i] in catch_list:
                        choices[i] = self.parents_dict[choices[i]]
                    big_choices[i].append(choices[i])
                cap += 1
        print(j)
        las_series = pd.Series(big_choices[1],  name='Lasair')
        alerce_series = pd.Series(big_choices[0], name='ALeRCE')
        fink_series = pd.Series(big_choices[2], name='Fink')
        df_confusion = pd.crosstab(las_series, alerce_series)
        self.confusion_plot(df_confusion)

    
    def large_con(self):
        targets = TargetList.objects.get(name='ALeRCE + Fink').targets.all()
        cap = 0
        j=0
        k=0
        sources = ['ALeRCE Stamp', 'Fink']#this is the order that the choices are arranged, make sure this is consistent with the assignment below
        big_choices = [[], [], []]
        for t in targets:
            tcs = t.targetclassification_set.all()#looks at all the associated target classifications and assesses the how many there are
            if cap < 50000:
                if t.targetextra_set.get(key='alerce_ndet').typed_value('number') < 10:
                    k+=1
                    continue
                #these lines pick the classification with the highest probability form each broker
                stamp_set = tcs.filter(level='lc_classifier').order_by('mjd', '-probability')
                if not stamp_set.exists():
                    stamp_set = tcs.filter(level='stamp_classifier_1.0.4').order_by('mjd', '-probability')
                if not stamp_set.exists():
                    stamp_set = tcs.filter(level='stamp_classifier_1.0.0').order_by('mjd', '-probability')
                if not stamp_set.exists():
                    j += 1
                    continue
                stamp_choice = self.alerce_codes[stamp_set[0].classification]
                if not tcs.filter(source='Fink').exists():
                    continue
                fink_choice = self.fink_codes[tcs.filter(source='Fink').order_by('mjd', '-probability')[0].classification]
                if fink_choice == '?':
                    continue
                catch_list = ['SN*', 'CV*', 'AGN', 'QSO', 'LP*', 'Ce*', 'RR*', 'dS*', 'Pu*', 'EB*', 'Y*O', 'V*', '?', 'SSO', 'Alert']
                choices = [stamp_choice, fink_choice]
                
                for i in range(len(choices)):
                    while not choices[i] in catch_list:
                        choices[i] = self.parents_dict[choices[i]]
                    big_choices[i].append(choices[i])
                cap += 1
        print(j,k)
        alerce_series = pd.Series(big_choices[0], name='ALeRCE')
        fink_series = pd.Series(big_choices[1], name='Fink')
        df_confusion = pd.crosstab(alerce_series, fink_series)
        print(df_confusion)
        self.confusion_plot(df_confusion)

    def confusion_plot(self, df_confusion):
        fig, ax = plt.subplots()
        ax.matshow(df_confusion, cmap='Blues')
        tick_marks = np.arange(len(df_confusion.columns))
        ax.set_xticks(tick_marks, df_confusion.columns, rotation=45)
        ax.set_yticks(tick_marks, df_confusion.index)
        #plt.tight_layout()
        ax.set_ylabel(df_confusion.index.name)
        ax.set_xlabel(df_confusion.columns.name)
        ax.tick_params(axis="x", bottom=True, top=False, labelbottom=True, labeltop=False)
        for (i, j), z in np.ndenumerate(df_confusion):
            ax.text(j, i, z, ha='center', va='center')
        fig.tight_layout()
        plt.show()

