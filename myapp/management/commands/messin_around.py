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

class Command(BaseCommand):

    help = 'This is a playground function so I can quickly test things out'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        mjd__gt = 59087 #minimum date
        mjd__lt = 59088 #maximum date

        today = 59765
        yesterday = 59764
        targets = TargetList.objects.get(name='Alerce + Fink + Lasair').targets.all()

        broker_pairs=['Alerce + Fink', 'Lasair + Fink', 'ALeRCE + Lasair']
        alfin_len = 85863
        lasfin_len = 84427
        allas_len = 53866
        fig = go.Figure(data=[
            go.Bar(name='Agree', x=broker_pairs, y=[42598/alfin_len, 36817/lasfin_len, 44658/allas_len], marker_color='lightgreen'),
            go.Bar(name='Disagree', x=broker_pairs, y=[43265/alfin_len, 47548/lasfin_len, 6706/allas_len], marker_color='tomato')
        ])
        # Change the bar mode
        fig.update_layout(barmode='group', title_text='Broker Agreement',yaxis_title='Decimal Agreement')
        fig.show()

        return 'Success!'

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

    def get_fink(self, mjd__gt, mjd__lt):
        st = time.time()
        fink_broker = FinkBroker()
        fink_alert_list_big = []

        dur = mjd__lt-mjd__gt
        offset = 0
        i = 0
        while offset < dur:# and len(fink_alert_list_big) < 50: #this line keeps fink from running all 25000, comment out before and
            t = Time(mjd__gt + offset,format = 'mjd')
            window = 3
            if offset + window/24 > dur:
                window = dur - offset
            query = {
                'objectId': '', 
                'conesearch': '', 
                'datesearch': f'{t.iso}, {window*60}',
                'classsearch': '', 
                'classsearchdate': '', 
                'ssosearch': ''
            }
            offset += 3/24

            fink_alerts = fink_broker.fetch_alerts(query)

            fink_alert_list = list(fink_alerts)
            for a in fink_alert_list:
                fink_alert_list_big.append(a)
            i+=1

        logging.info(f'Fink took {time.time() - st } sec to gather {len(fink_alert_list_big)} alerts')
        return fink_alert_list_big
