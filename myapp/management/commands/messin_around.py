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

        # self.plot_lc('ZTF17aadevsj')#, period=0.143436278964915)
        # # self.plot_lc('ZTF17aadevsj', period=0.143436278964915)
        # # self.plot_lc('ZTF18aainbqt')#, period=0.580542615750098)
        # self.plot_lc('ZTF18aainbqt', period=0.580542615750098)
        self.plot_lc('ZTF19abcelqj')
        # # self.plot_lc('ZTF22aajijjf')
        # self.plot_lc('ZTF18aainbrb')
        # self.plot_lc('ZTF18aainbrb',period=0.09201468191595663)
        # df = pd.read_fwf(path.join(settings.MEDIA_ROOT,'ZTF21abhibro/tns.spec'))
        # print(df)
        # fig, ax = plt.subplots(figsize=(15,4))
        # ax.plot(df['wavelen'], df['flux'])
        # ax.set_xlabel(r"Observed Wavelength [Angstrom $\AA$]")
        # ax.set_ylabel('Flux')
        # ax.set_title('Observed Spectra')
        # plt.show()
        self.plot_lc('ZTF21abhibro')


        # webbrowser.open("",new=1)
        # length = 50
        # offset = 800
        # targets = TargetList.objects.get(name='Alerce + Fink + Lasair').targets.all()[offset:offset+length]
        # for t in targets:
        #     fink_choice = t.targetclassification_set.filter(source='Fink').order_by('mjd', '-probability')[0].classification
        #     if fink_choice == 'Unknown' or fink_choice == 'RRLyr' or 'LP*' in fink_choice:
        #         continue
        #     alerce_set = t.targetclassification_set.filter(source='ALeRCE', level='lc_classifier')
        #     if alerce_set.exists():
        #         alerce_choice = alerce_set.order_by('mjd', '-probability')[0].classification
        #     else:
        #         continue

        #     if not alerce_choice == fink_choice:
        #         webbrowser.open(f"http://127.0.0.1:8000/targets/name/{t.name}")

            
            # if 'EB' in t.targetextra_set.get(key='fink_v:classification').typed_value(''):
            #     print(fink_choice)
            #     webbrowser.open(f"http://127.0.0.1:8000/targets/name/{t.name}")




        return 'Success!'
    def plot_lc(self, name, period=None):
        file_name = f'{name}/detections.csv'
        df = pd.read_csv(path.join(settings.MEDIA_ROOT,file_name))
        if period:
            mod_series = df['mjd'] % (2*period)
            df['mjd'] = mod_series
        df['fid'] = np.where(df['fid']==1,'g','r')
        print(df)
        fig, ax = plt.subplots(figsize=(15,6))
        ax.scatter(df['mjd'], df['magpsf'],c=df['fid'], s=8)
        ax.invert_yaxis()
        if period:
            ax.set_xlabel('Phase [Days]',fontsize=18)
        else:
            ax.set_xlabel('MJD',fontsize=18)
        ax.set_ylabel('Corrected Magnitude',fontsize=18)
        if period:
            ax.set_title(f'Period of {np.round(period,3)} days')
            plt.savefig(f'/home/bmills/Pictures/light curves/{name}Fold.png', dpi=300)
        else:
            plt.savefig(f'/home/bmills/Pictures/light curves/{name}.png', dpi=300)
        fig.suptitle(name,fontsize=24)
        plt.savefig(f'/home/bmills/Pictures/light curves/{name}.png', dpi=300)
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


