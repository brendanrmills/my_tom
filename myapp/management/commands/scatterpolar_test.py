    
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
        i=1
        target= test_targets[i]
        tcs = target.targetclassification_set.all()
        
        alerce_lc_tcs = tcs.filter(level='lc_classifier')
        alerce_stamp_tcs= tcs.filter(level='stamp_classifier_1.0.4')
        if len(alerce_stamp_tcs) == 0:
            alerce_stamp_tcs = tcs.filter(level='stamp_classifier_1.0.0')
        lasair_tcs = tcs.filter(source='Lasair')
        fink_tcs = tcs.filter(source='Fink')

        with open('/home/bmills/bmillsWork/tom_test/mytom/variability.txt') as json_file:
            parents_dict = json.load(json_file)
        
        fig = go.Figure(go.Barpolar(
            r=[1,1,1,1,1,1,1],
            theta=['AGN', 'SNII', 'RR*', 'Y*O','ast', 'Other'],
            width=[3, 5, 5, 7, 1, 3],
            marker_color=["#E4FF87", '#709BFF', '#B6FFB4', '#FFAA70', '#F242F5','#424142'],
            opacity=0.15,
            hovertext=['AGN Types', 'Supernovae', 'Pulsating', 'Stellar Variability', 'Asteroid', 'Other Variability'],
            hoverinfo='text',
            name='Groupings'
        ))
        fig.add_trace(go.Barpolar(
            r=[.1,.1,.1,.1,.1,.1],
            theta=['AGN', 'SNII', 'RR*', 'Y*O','ast', 'Other'],
            width=[3, 5, 5, 7, 1, 3],
            marker_color=["#E4FF87", '#709BFF', '#B6FFB4', '#FFAA70', '#F242F5','#424142'],
            opacity=0.8,
            hovertext=['AGN Types', 'Supernovae', 'Pulsating', 'Stellar Variability', 'Asteroid', 'Other Variability'],
            hoverinfo='text',
            base=np.ones(6)
        ))
        objs = ['SNIa', 'SNIbc', 'SNII', 'SLSN', 'SN*', 'QSO', 'AGN', 'G*', 'LP*', 'Ce*', 'RR*', 'dS*', 'Pu*', 'EB*', 'CV*', '**',  'Y*O', 'Er*', 'Ro*', 'V*', 'ast', 'grv', 'Other', 'Alert']
        
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
        
        if lasair_tcs:
            tc = lasair_tcs[len(lasair_tcs)-1]
            code_walker = las_codes[tc.classification]
            while not code_walker in objs:
                code_walker = parents_dict[code_walker]
            l_code = code_walker
            l_prob = tc.probability
            fig.add_trace(go.Barpolar(
                name="Lasair",
                r=[l_prob],
                theta=[l_code],
                width=[1],
                marker= dict(line_width=2, line_color='green', color='rgba(0,0,0,0)',),
                base=0,
                hovertext=['Lasair: ' + tc.classification],
                hoverinfo='text',
            ))
        
        # deals with alerce stamp
        alst_codes = {
            'SN': 'SN*',
            'AGN': 'AGN',
            'VS': 'V*',
            'bogus': 'err',
            'asteroid': 'ast',
        }
        alst_list = []
        alst_probs = []
        for tc in alerce_stamp_tcs:
            code_walker = alst_codes[tc.classification]
            while not code_walker in objs:
                code_walker = parents_dict[code_walker]
            alst_list.append(code_walker)
            alst_probs.append(tc.probability)

        fig.add_trace(go.Barpolar(#alerce stamp bar chart
            name='ALeRCE Stamp',
            r=alst_probs,
            theta=alst_list,
            width=np.ones(5),
            marker_color='#BB8FCE',
            marker_line_color="black",
            marker_line_width=2,
            opacity=0.8,
            base=0,
            ))

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
            'Periodic-Other': 'Pu*',
        }
        alerce_lc_cats = []
        alerce_lc_probs = []
        for tc in alerce_lc_tcs:
            code_walker = allc_codes[tc.classification]
            while not code_walker in objs:
                code_walker = parents_dict[code_walker]
            alerce_lc_cats.append(code_walker)
            alerce_lc_probs.append(tc.probability)

        lc_out = []
        lc_out_p = []
        for o in objs:#this reorders the list to make the output nicer
            try:
                i = alerce_lc_cats.index(o)
                lc_out.append(alerce_lc_cats[i])
                lc_out_p.append(alerce_lc_probs[i])
            except:
                pass
        fig.add_trace(go.Scatterpolar(
            name='ALeRCE LC',
            r=lc_out_p,
            theta=lc_out,
            line=dict(color='#8E44AD', width=2),
            opacity=0.8,
            fill = 'toself'
        ))
        
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

        #deals with fink,
        if fink_tcs:
            candidate = 'Candidate' in tc.classification or 'candidate' in tc.classification
            if candidate:
                fig.add_annotation(x=1,y=.98,text='This is a candidate target',showarrow=False)
            fink_cats = []
            fink_probs = []
            offset = 0
            for tc in fink_tcs:
                if tc.probability < 0.01:
                    continue
                code_walker = fink_codes[tc.classification]
                print(tc.classification)
                while not code_walker in objs:
                    code_walker = parents_dict[code_walker]
                if not code_walker == tc.classification:
                    offset += 0.05
                    fig.add_annotation(x=1,y=1.1-offset,
                    text='Fink actually thinks this is ' + tc.classification,
                    showarrow=False,)
                fink_cats.append(code_walker)
                fink_probs.append(tc.probability)
            fig.add_trace(go.Scatterpolar(
                name='Fink',
                r=fink_probs,
                theta=fink_cats,
                line=dict(color='#EB984E', width=2),
                opacity=0.8,
            ))

        fig.update_layout(
            template=None,
            height=800,
            width=800,
            polar = dict(
                # radialaxis = dict(showticklabels=False, ticks=''),
                angularaxis = dict(
                    categoryarray=objs,
                    categoryorder='array',
                    showticklabels=True,
                    )
            )
        )
        fig.show()