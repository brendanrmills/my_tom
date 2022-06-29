from heapq import merge
from django.test import TestCase
from django.core.management.base import BaseCommand
from tom_targets.models import Target
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker

from tom_targets.models import Target, TargetName
from merge_methods import merge_streams, get_duplicates

# mars_alert = {
#     'candid': 617122521615015023,
#     'candidate': {
#        'b': 0.70548695469711,
#        'dec': -10.5296018,
#        'jd': 2458371.6225231,
#        'l': 20.7124513780029,
#        'magpsf': 16.321626663208,
#        'ra': 276.5843017,
#        'rb': 0.990000009536743,
#        'wall_time': 'Mon, 10 Sep 2018 02:56:25 GMT',
#     },
#     'lco_id': 11296149,
#     'objectId': 'ZTF18abbkloa',
# }
mars_alert1 = {
        "candid":1771468511015015012,
        "candidate":{
            "aimage":0.742999970912933,
            "aimagerat":0.355502396821976,
            "b":30.3681440334,
            "bimage":0.705999970436096,
            "bimagerat":0.337799042463303,
            "candid":1771468511015015012,
            "chinr":1.04799997806549,
            "chipsf":29.7098903656006,
            "classtar":0.735000014305115,
            "clrcoeff":-0.111790999770164,
            "clrcounc":8.92519983608508e-06,
            "clrmed":0.649999976158142,
            "clrrms":0.301896005868912,
            "dec":30.2484668,
            "decnr":30.2484498,
            "deltamaglatest":-0.441526412963867,
            "deltamagref":-1.8599739074707,
            "diffmaglim":20.8421020507812,
            "distnr":0.287732243537903,
            "distpsnr1":0.259824395179749,
            "distpsnr2":9.3966646194458,
            "distpsnr3":10.0376224517822,
            "drb":0.996207475662231,
            "drbversion":"d6_m7",
            "dsdiff":-87.3517227172852,
            "dsnrms":72.8019027709961,
            "elong":1.05240797996521,
            "exptime":30.0,
            "fid":1,
            "field":664,
            "filter":"g",
            "fwhm":2.08999991416931,
            "isdiffpos":"t",
            "jd":2459525.9685185,
            "jdendhist":2459525.9685185,
            "jdendref":2458431.974549,
            "jdstarthist":2458042.0100347,
            "jdstartref":2458166.745799,
            "l":192.088191906821,
            "magap":17.6721992492676,
            "magapbig":17.672399520874,
            "magdiff":0.0372270010411739,
            "magfromlim":3.16990208625793,
            "maggaia":15.2180509567261,
            "maggaiabright":13.5671796798706,
            "magnr":15.7749996185303,
            "magpsf":17.634973526001,
            "magzpsci":26.4199733734131,
            "magzpscirms":0.0424209982156754,
            "magzpsciunc":5.56399982087896e-06,
            "mindtoedge":807.5419921875,
            "nbad":0,
            "ncovhist":1228,
            "ndethist":699,
            "neargaia":0.265789598226547,
            "neargaiabright":70.2278747558594,
            "nframesref":15,
            "nid":1771,
            "nmatches":812,
            "nmtchps":6,
            "nneg":3,
            "objectidps1":144291238860108795,
            "objectidps2":144291238842156311,
            "objectidps3":144291238842615939,
            "pdiffimfilename":"ztf_20211107468484_000664_zg_c03_o_q3_scimrefdiffimg.fits",
            "pid":1771468511015,
            "programid":1,
            "programpi":"Kulkarni",
            "ra":123.8860736,
            "ranr":123.8859826,
            "rb":0.937142848968506,
            "rbversion":"t17_f5_c3",
            "rcid":10,
            "rfid":664120110,
            "scorr":27.5910549163818,
            "seeratio":1.29505753517151,
            "sgmag1":16.003999710083,
            "sgmag2":-999.0,
            "sgmag3":-999.0,
            "sgscore1":0.993809998035431,
            "sgscore2":0.0,
            "sgscore3":0.5,
            "sharpnr":-0.0209999997168779,
            "sigmagap":0.0292000006884336,
            "sigmagapbig":0.0331999994814396,
            "sigmagnr":0.0149999996647239,
            "sigmapsf":0.0549394935369492,
            "simag1":15.0401000976562,
            "simag2":20.6604995727539,
            "simag3":-999.0,
            "sky":-0.00695581501349807,
            "srmag1":15.0651998519897,
            "srmag2":21.3115997314453,
            "srmag3":21.7278995513916,
            "ssdistnr":-999.0,
            "ssmagnr":-999.0,
            "ssnamenr":'101816',
            "ssnrms":160.153625488281,
            "sumrat":0.999431192874908,
            "szmag1":15.1532001495361,
            "szmag2":20.4062995910645,
            "szmag3":-999.0,
            "tblid":12,
            "tooflag":0,
            "wall_time":"Sun, 07 Nov 2021 11:14:39 GMT",
            "xpos":1814.24426269531,
            "ypos":807.5419921875,
            "zpclrcov":-6.50999982099165e-06,
            "zpmed":26.3479995727539
        },
        "lco_id":265713780,
        "objectId":"ZTF17aadevsj",
}

mars_alert2 = {
        "candid":1771468511015015012,
        "candidate":{
            "aimage":0.742999970912933,
            "aimagerat":0.355502396821976,
            "b":30.3681440334,
            "bimage":0.705999970436096,
            "bimagerat":0.337799042463303,
            "candid":1771468511015015012,
            "chinr":1.04799997806549,
            "chipsf":29.7098903656006,
            "classtar":0.735000014305115,
            "clrcoeff":-0.111790999770164,
            "clrcounc":8.92519983608508e-06,
            "clrmed":0.649999976158142,
            "clrrms":0.301896005868912,
            "dec":30.2484668,
            "decnr":30.2484498,
            "deltamaglatest":-0.441526412963867,
            "deltamagref":-1.8599739074707,
            "diffmaglim":20.8421020507812,
            "distnr":0.287732243537903,
            "distpsnr1":0.259824395179749,
            "distpsnr2":9.3966646194458,
            "distpsnr3":10.0376224517822,
            "drb":0.996207475662231,
            "drbversion":"d6_m7",
            "dsdiff":-87.3517227172852,
            "dsnrms":72.8019027709961,
            "elong":1.05240797996521,
            "exptime":30.0,
            "fid":1,
            "field":664,
            "filter":"g",
            "fwhm":2.08999991416931,
            "isdiffpos":"t",
            "jd":2459525.9685185,
            "jdendhist":2459525.9685185,
            "jdendref":2458431.974549,
            "jdstarthist":2458042.0100347,
            "jdstartref":2458166.745799,
            "l":192.088191906821,
            "magap":17.6721992492676,
            "magapbig":17.672399520874,
            "magdiff":0.0372270010411739,
            "magfromlim":3.16990208625793,
            "maggaia":15.2180509567261,
            "maggaiabright":13.5671796798706,
            "magnr":15.7749996185303,
            "magpsf":17.634973526001,
            "magzpsci":26.4199733734131,
            "magzpscirms":0.0424209982156754,
            "magzpsciunc":5.56399982087896e-06,
            "mindtoedge":807.5419921875,
            "nbad":0,
            "ncovhist":1228,
            "ndethist":699,
            "neargaia":0.265789598226547,
            "neargaiabright":70.2278747558594,
            "nframesref":15,
            "nid":1771,
            "nmatches":812,
            "nmtchps":6,
            "nneg":3,
            "objectidps1":144291238860108795,
            "objectidps2":144291238842156311,
            "objectidps3":144291238842615939,
            "pdiffimfilename":"ztf_20211107468484_000664_zg_c03_o_q3_scimrefdiffimg.fits",
            "pid":1771468511015,
            "programid":1,
            "programpi":"Kulkarni",
            "ra":123.8860736,
            "ranr":123.8859826,
            "rb":0.937142848968506,
            "rbversion":"t17_f5_c3",
            "rcid":10,
            "rfid":664120110,
            "scorr":27.5910549163818,
            "seeratio":1.29505753517151,
            "sgmag1":16.003999710083,
            "sgmag2":-999.0,
            "sgmag3":-999.0,
            "sgscore1":0.993809998035431,
            "sgscore2":0.0,
            "sgscore3":0.5,
            "sharpnr":-0.0209999997168779,
            "sigmagap":0.0292000006884336,
            "sigmagapbig":0.0331999994814396,
            "sigmagnr":0.0149999996647239,
            "sigmapsf":0.0549394935369492,
            "simag1":15.0401000976562,
            "simag2":20.6604995727539,
            "simag3":-999.0,
            "sky":-0.00695581501349807,
            "srmag1":15.0651998519897,
            "srmag2":21.3115997314453,
            "srmag3":21.7278995513916,
            "ssdistnr":-999.0,
            "ssmagnr":-999.0,
            "ssnamenr":"null",
            "ssnrms":160.153625488281,
            "sumrat":0.999431192874908,
            "szmag1":15.1532001495361,
            "szmag2":20.4062995910645,
            "szmag3":-999.0,
            "tblid":12,
            "tooflag":0,
            "wall_time":"Sun, 07 Nov 2021 11:14:39 GMT",
            "xpos":1814.24426269531,
            "ypos":807.5419921875,
            "zpclrcov":-6.50999982099165e-06,
            "zpmed":26.3479995727539
        },
        "lco_id":11053318,
        "objectId":"ZTF18aberpsh",
}

antares_alert1 = {
    'locus_id' : 1,
    'ra' : 2,
    'dec' : 3,
    'properties' : {
        'ztf_object_id' : "ZTF17aadevsj",
        'num_alerts' : 4
    },
    'tags' : ['lc_feature_extractor'],
    'catalogs' : [],
    'alerts' : []
    }

antares_alert2 = {
'locus_id' : 1,
'ra' : 2,
'dec' : 3,
'properties' : {
    'ztf_object_id' : 'ZTF18aberpsh',
    'num_alerts' : 4
},
'tags' : ['lc_feature_extractor'],
'catalogs' : [],
'alerts' : []
}
mars_alert_stream = []
antares_alert_stream = []
names = ['ZTF18aberpsh', 'ZTF17aadevsj']

class AlertComboTestCase(TestCase):
    def setUp(self):
        self.mars_alert_stream = iter([mars_alert1, mars_alert2])
        self.antares_alert_stream = iter([antares_alert2, antares_alert1])
        self.names = names


    def test_alertcombo(self):
        # this code was just copied from the save_data.py file
        mars_alerts = list(self.mars_alert_stream)
        
        # start an antares broker and geth the alerts
        antares_alerts = list(self.antares_alert_stream)
        
        merge_streams([mars_alerts, antares_alerts])
        targets = list(Target.objects.all())

        target_names = []
        for t in targets:
            target_names.append(t.name)
        
        for n in target_names:
            self.assertIn(n, self.names)

        dups = get_duplicates(targets)
        print(dups)
        self.assertEqual(len(dups),2)


        
        
