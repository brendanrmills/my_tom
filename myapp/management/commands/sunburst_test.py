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
        target = Target.objects.get(name='ZTF21abkrdax')
        tcs = target.targetclassification_set.all()
        alerce_lc_tcs = tcs.filter(level='lc_classifier')
        alerce_stamp_tcs= tcs.filter(level='stamp_classifier_1.0.4')
        if len(alerce_stamp_tcs) == 0:
            alerce_stamp_tcs = tcs.filter(level='stamp_classifier_1.0.0')
        lasair_tcs = tcs.filter(source='Lasair')
        fink_tcs = tcs.filter(source='Fink')

        objs = ['Bogus', 'Asteroid', 'Solar System Object', 'YSO', 'CV/Nova', 'Microlensing', 'Eclipsing Binary', 'Rotating', 'SNIa', 'SNIb/c', 'SNII', 'SLSN', 'SN Other', 'Blazar', 'Quasar', 'AGN Other', 'LPV', 'Cepheid', 'RR Lyrae', 'del Scuti', 'Variable Other', 'Other', 'Unknown']
        fig = go.Figure(go.Barpolar(
            r=[1,1,1,1,1],
            theta=['Quasar', 'SNII', 'RR Lyrae', 'Bogus', 'Microlensing'],
            width=[3, 5, 5, 5, 5],
            marker_color=["#E4FF87", '#709BFF', '#B6FFB4', '#FFAA70', '#FFDF70'],
            opacity=0.15,
            hovertext=['AGN Types', 'Supernovae', 'Pulsating', 'Other', 'Extrinisc Variability'],
            hoverinfo='text',
            name='Groupings'
        ))
        fig.add_trace(go.Barpolar(
            r=[.1,.1,.1,.1,.1],
            theta=['Quasar', 'SNII', 'RR Lyrae', 'Bogus', 'Microlensing'],
            width=[3, 5, 5, 5, 5],
            marker_color=["#E4FF87", '#709BFF', '#B6FFB4', '#FFAA70', '#FFDF70'],
            opacity=0.8,
            hovertext=['AGN Types', 'Supernovae', 'Pulsating', 'Other', 'Extrinisc Variability'],
            hoverinfo='text',
            name='Groupings',
            base=np.ones(5)
        ))

        label_to_code = {}
        with open('/home/bmills/bmillsWork/tom_test/mytom/SIMBAD_otypes_labels.txt') as f:
            for line in f:
                [_, code, old, new] = line.split('|')
                label_to_code[old.strip()] = code.strip()
                label_to_code[new.strip()] = code.strip()

        fig = go.Figure(
            data=[go.Bar(y=[2, 1, 5])],
            layout_title_text="A Figure Displayed with fig.show()"
        )
        fig.show()
        mapping_dict = {#this dictionary provides mappinf from the broker classifications to the diagram wedges
            #Lasair classifs
            'Lasair VS': ('RR Lyrae', 5),
            'Lasair CV': ('CV/Nova', 1),
            'Lasair SN': ('SNII', 5),
            'Lasair ORPHAN': ('Unknown', 1),
            'Lasair AGN': ('Quasar', 3),
            'Lasair NT': ('AGN Other', 1),
            'ALeRCEs bogus': ('Bogus', 1),
            'ALeRCEs asteroid': ('Asteroid', 1),
            'ALeRCEs VS': ('RR Lyrae', 5),
            'ALeRCEs SN': ('SNII', 5),
            'ALeRCEs AGN': ('Quasar', 3),
            'ALeRCE E': 'Eclipsing Binary',
            'ALeRCE RRL': 'RR Lyrae',
            'ALeRCE DSCT': 'del Scuti',
            'ALeRCE CEP': 'Cepheid',
            'ALeRCE QSO': 'Quasar',
            'ALeRCE Not classified': 'Unknown',
            'ALeRCE AGN': 'AGN Other',
            'ALeRCE SNIbc': 'SNIb/c',
            'ALeRCE Periodic-Other': 'Variable Other',
            'Fink fink_mulens': 'Microlensing',
            'Fink fink_sso': 'Solar System Object',
            'Fink fink_KN': 'SN Other',
            'Fink QSO': 'Quasar',
            'Fink EB*': 'Eclipsing Binary',
            'Fink fink_SNIa': 'SNIa'

        }
        with open('/home/bmills/bmillsWork/tom_test/tom_base/tom_targets/templatetags/classif_printout.txt') as json_file:
            data = json.load(json_file)
        mapping_dict.update(data)
        #delas with lasair
        las_codes = {#still need to handle bright star
            'VS': 'V*',
            'CV': 'CV*',
            'SN': 'SN*',
            'ORPHAN': 'unk',
            'AGN': 'AGN',
            'NT': 'Transient',
        }
        if lasair_tcs:
            tc = lasair_tcs[len(lasair_tcs)-1]


        if lasair_tcs:#checks to make sure there are lasair classifications
            tc = lasair_tcs[len(lasair_tcs)-1]
            las_cat = mapping_dict[tc.source + ' ' + tc.classification][0]
            las_prob = tc.probability
            las_width = mapping_dict[tc.source + ' ' + tc.classification][1]
            fig.add_trace(go.Barpolar(
                name="Lasair",
                r=[1],
                theta=[las_cat],
                width=[las_width],
                marker= dict(line_width=2, line_color='green', color='rgba(0,0,0,0)',),
                base=0,
                hovertext=['Lasair: ' + tc.classification],
                hoverinfo='text',
            ))
        # deals with alerce stamp 
        alerce_stamp_cats = []
        alerce_stamp_probs = []
        alerce_stamp_widths = []
        for tc in alerce_stamp_tcs:
            alerce_stamp_cats.append(mapping_dict[tc.source + 's ' + tc.classification][0])
            alerce_stamp_widths.append(mapping_dict[tc.source + 's ' + tc.classification][1])
            alerce_stamp_probs.append(tc.probability)

        fig.add_trace(go.Barpolar(#alerce stamp bar chart
            name='ALeRCE Stamp',
            r=alerce_stamp_probs,
            theta=alerce_stamp_cats,
            width=alerce_stamp_widths,
            marker_color='#BB8FCE',
            marker_line_color="black",
            marker_line_width=2,
            opacity=0.8,
            base=0,
            ))

        #does alerce lc
        alerce_lc_cats = []
        alerce_lc_probs = []
        for tc in alerce_lc_tcs:
            try:
                alerce_lc_cats.append(mapping_dict[tc.source + ' ' + tc.classification])
                alerce_lc_probs.append(tc.probability)
            except:
                alerce_lc_cats.append(tc.classification)
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
        if fink_tcs:
            tc = fink_tcs[len(fink_tcs)-1]
            candidate = 'Candidate' in tc.classification or 'candidate' in tc.classification
            fink_cats = []
            fink_probs = []
            for tc in fink_tcs:
                try:
                    fink_cats.append(mapping_dict[tc.source + ' ' + tc.classification])
                    fink_probs.append(tc.probability)
                except:
                    fink_cats.append(tc.classification)
                    fink_probs.append(tc.probability)
                if fink_cats[-1] in ['Other', 'AGN Other', 'Variable Other', 'SN Other'] and fink_probs[-1]>0.5:
                    fig.add_annotation(x=-0.1,y=1.1,
                    text='Fink Classification: ' + tc.classification,
                    showarrow=False,
                    )
            fig.add_trace(go.Scatterpolar(
                name='Fink',
                r=fink_probs,
                theta=fink_cats,
                line=dict(color='#EB984E', width=2),
                opacity=0.8,
            ))


        fig.update_layout(
            template=None,
            polar = dict(
                # radialaxis = dict(showticklabels=False, ticks=''),
                angularaxis = dict(
                    categoryarray=objs,
                    categoryorder='array',
                    showticklabels=True,
                    )
            )
        )
        # ring_prob = [None, 0.15, 0.05, 0.75, 0.05, 0]
        # to_add = [
        #     ['Quasar'],
        #     ['AGN'],
        #     [5],
        #     [.85]
        # ]
        # fig =go.Figure(go.Sunburst(
        #     labels=[target.name, 'Extrinsic Variability', 'Supernova', 'AGN', 'Pulsating', 'Other'] + to_add[0],
        #     parents=['', target.name,  target.name, target.name, target.name, target.name, ] + to_add[1],
        #     values=[None, 14, 12, 10, 2, 6] + to_add[2],
        #     marker=dict(
        #         colors=ring_prob + to_add[3],
        #         colorscale='Greens',
        #         cmid=0.5),
        #         hovertemplate='<b>%{label} </b> <br> Probability: %{color}',
        # ))
        # fig.update_layout(
        #     margin = dict(t=0, l=0, r=0, b=0),
        #     height=height,
        #     width=width,)

        fig.show()

        return 'Success!'