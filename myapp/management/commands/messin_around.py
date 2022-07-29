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
import webbrowser
import numpy as np
import pandas as pd
from os import path
from django.conf import settings
import matplotlib.pyplot as plt

class Command(BaseCommand):

    help = 'This is a playground function so I can quickly test things out'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        mjd__gt = 59087 #minimum date
        mjd__lt = 59088 #maximum date

        today = 59765
        yesterday = 59764
        self.plot_lc('ZTF17aadevsj', 'detections.csv', period=0.143436278964915)


        # webbrowser.open("",new=1)
        # length = 2000
        # offset = 190
        # targets = TargetList.objects.get(name='Alerce + Fink + Lasair').targets.all()[offset:offset+length]
        # for t in targets:
        #     fink_choice = t.targetclassification_set.filter(source='Fink').order_by('mjd', '-probability')[0].classification

        #     if fink_choice == 'Unknown' or fink_choice == 'RRLyr' or 'EB*' in fink_choice or 'LP*' in fink_choice:
        #         continue
        #     if 'SN' in t.targetextra_set.get(key='fink_v:classification').typed_value(''):
        #         print(fink_choice)
        #         webbrowser.open(f"http://127.0.0.1:8000/targets/name/{t.name}")



        # tcs = TargetClassification.objects.filter(source='Fink')
        # i=0
        # l = len(tcs)
        # for j, tc in enumerate(tcs):
        #     if tc.classification == 'Unknown':
        #         i+=1
        #     printProgressBar(j+1, l, prefix = 'Fink TCs:', suffix = 'Complete', length = 50)
        # print(l, i)
        # broker_pairs=['Alerce + Fink', 'Lasair + Fink', 'ALeRCE + Lasair']
        # alfin_len = 85863
        # lasfin_len = 84427
        # allas_len = 53866
        # fig = go.Figure(data=[
        #     go.Bar(name='Agree', x=broker_pairs, y=[42598/alfin_len, 36817/lasfin_len, 44658/allas_len], marker_color='lightgreen'),
        #     go.Bar(name='Disagree', x=broker_pairs, y=[43265/alfin_len, 47548/lasfin_len, 6706/allas_len], marker_color='tomato')
        # ])
        # # Change the bar mode
        # fig.update_layout(barmode='group', title_text='Broker Agreement',yaxis_title='Decimal Agreement')
        # fig.show()

        return 'Success!'
    def plot_lc(self, name, file_name, period=None):
        df = pd.read_csv(path.join(settings.MEDIA_ROOT,file_name))
        if period:
            mod_series = df['mjd'] % (2*period)
            df['mjd'] = mod_series
        df['fid'] = np.where(df['fid']==1,'g','r')

        fig, ax = plt.subplots(figsize=(10,5))
        ax.scatter(df['mjd'], df['magpsf_corr'],c=df['fid'], s=8)
        ax.invert_yaxis()
        if period:
            ax.set_xlabel('Days mod Period')
        else:
            ax.set_xlabel('MJD')
        ax.set_ylabel('Corrected Magnitude')
        if period:
            ax.set_title(f'Period of {period} days')
        fig.suptitle(name)
        plt.show()

    # Print iterations progress
    def printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        # Print New Line on Complete
        if iteration == total: 
            print()


