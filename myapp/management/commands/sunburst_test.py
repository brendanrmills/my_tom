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
from dateutil.parser import parse
from urllib.parse import urlencode
from plotly import offline
from plotly.subplots import make_subplots
from plotly import graph_objs as go
import numpy as np

class Command(BaseCommand):

    help = 'This is a playground function so I can quickly test things out'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        targets = TargetList.objects.get(name='Alerce + Fink + Lasair').targets.all()
        test_targets = []
        i = 0
        for t in targets:
            if i>1:
                break
            if len(t.targetclassification_set.all()) > 8:
                test_targets.append(t)
                i+=1
        # target = Target.objects.get(name='ZTF19ablwmjh')
        for i in range(len(test_targets)):
            target= test_targets[i]
            tcs = target.targetclassification_set.all()
            
            alerce_lc_tcs = tcs.filter(level='lc_classifier')
            alerce_stamp_tcs= tcs.filter(level='stamp_classifier_1.0.4')
            if len(alerce_stamp_tcs) == 0:
                alerce_stamp_tcs = tcs.filter(level='stamp_classifier_1.0.0')
            lasair_tcs = tcs.filter(source='Lasair')
            fink_tcs = tcs.filter(source='Fink')

            #delas with lasair
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
            codes = []
            if lasair_tcs:
                tc = lasair_tcs[len(lasair_tcs)-1]
                l_code = las_codes.get(tc.classification)
                codes.append( (l_code, 'Lasair', tc.probability) )

            # deals with alerce stamp
            alst_codes = {
                'SN': 'SN*',
                'AGN': 'AGN',
                'VS': 'V*',
                'bogus': 'err',
                'asteroid': 'ast',
            } 
            for tc in alerce_stamp_tcs:
                codes.append( (alst_codes.get(tc.classification), 'Alerce stamp', tc.probability))

            #does alerce lc
            allc_codes = {
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
                'Perodic Other': 'Pu*',
            }
            for tc in alerce_lc_tcs:
                codes.append( (allc_codes.get(tc.classification), 'Alerce LC', tc.probability))
                
            #deals with fink,
            candidate = 'candidate' in tc.classification or 'Candidate' in tc.classification
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
            with open('/home/bmills/bmillsWork/tom_test/mytom/SIMBAD_otypes_labels.txt') as f:
                for line in f:
                    [_, code, old, new] = line.split('|')
                    fink_codes[old.strip()] = code.strip()
                    fink_codes[new.strip()] = code.strip()
            
            for tc in fink_tcs:
                codes.append( (fink_codes[tc.classification], 'Fink', tc.probability))

            with open('/home/bmills/bmillsWork/tom_test/mytom/variability.txt') as json_file:
                parents_dict = json.load(json_file)

            labels = ['Alert']
            parents = ['']
            values = [None]
            colors = [0]
            for code in codes:
                code_walker = code[0]
                confidence = code[2] #this is not statistical confidence more like a relative feeling
                if confidence < 0.01:
                    continue
                lineage = [(code_walker, confidence)]
                while code_walker and code_walker != 'Alert':#this loop builds the lineage
                    code_walker = parents_dict[code_walker]
                    lineage.append( (code_walker, confidence) )
                lineage.append(('',-1))
                for l in lineage:
                    if not l[0]:
                        break
                    if l[0] == 'Alert':
                        continue
                    if l[0] in labels:
                        colors[labels.index(l[0])] += l[1]
                    else:
                        labels.append(l[0])
                        parents.append(parents_dict[l[0]])
                        values.append(1)
                        colors.append(l[1])

            fig =go.Figure(go.Sunburst(
                labels=labels,
                parents=parents,
                values=colors,
                marker=dict(
                    colors=colors,
                    colorscale='Greens',
                    colorbar=dict(
                        tick0=0,
                        len=0.25
                        )),
            ))

            fig.update_layout(
                title={
                    'text': target.name,
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                margin = dict(t=100, l=0, r=0, b=0),
                height=800,
                width=800,)
            fig.show()


        return 'Success!'