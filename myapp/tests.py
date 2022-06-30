from django.test import TestCase
from django.core.management.base import BaseCommand
from tom_targets.models import Target
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker

from tom_targets.models import Target, TargetName
from merge_methods import *
import copy

mars_alert = {
   "avro": "https://s3.us-west-2.amazonaws.com/ztf-alert.lco.global/2020/08/26/1333493791415015001.avro?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA6FT4CXR4XPDC3WKJ%2F20220629%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220629T173100Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=2043fd88a6cfebf9a73e85c9b816c3ad8d59eecd743c8e605fb05ef72c94625c",
   "candid": 1333493791415015001,
   "candidate": {
      "aimage": 0.670000016689301,
      "aimagerat": 0.285106390714645,
      "b": -16.3841533109491,
      "bimage": 0.563000023365021,
      "bimagerat": 0.239574462175369,
      "candid": 1333493791415015001,
      "chinr": 0.941999971866608,
      "chipsf": 21.1832828521729,
      "classtar": 0.852999985218048,
      "clrcoeff": -0.0768250003457069,
      "clrcounc": 8.91390027391026e-06,
      "clrmed": 0.720000028610229,
      "clrrms": 0.204610005021095,
      "dec": 37.5694793,
      "decnr": 37.569503,
      "deltamaglatest": 0.279788970947266,
      "deltamagref": -1.95818901062012,
      "diffmaglim": 20.4428329467773,
      "distnr": 0.144495874643326,
      "distpsnr1": 0.0914967507123947,
      "distpsnr2": 18.7441635131836,
      "distpsnr3": 20.5170021057129,
      "drb": 0.997780203819275,
      "drbversion": "d6_m7",
      "dsdiff": -112.151840209961,
      "dsnrms": 95.90185546875,
      "elong": 1.19005334377289,
      "exptime": 30.0,
      "fid": 1,
      "field": 700,
      "filter": "g",
      "fwhm": 2.34999990463257,
      "isdiffpos": "t",
      "jd": 2459087.9937963,
      "jdendhist": 2459087.9937963,
      "jdendref": 2458428.799178,
      "jdstarthist": 2458131.6116088,
      "jdstartref": 2458168.623461,
      "l": 153.080347527292,
      "magap": 16.9097003936768,
      "magapbig": 16.8969993591309,
      "magdiff": 0.0205119997262955,
      "magfromlim": 3.53313398361206,
      "maggaia": 14.1421527862549,
      "maggaiabright": -999.0,
      "magnr": 14.9309997558594,
      "magpsf": 16.8891887664795,
      "magzpsci": 25.976188659668,
      "magzpscirms": 0.0313530005514622,
      "magzpsciunc": 5.68489986108034e-06,
      "mindtoedge": 30.1760997772217,
      "nbad": 0,
      "ncovhist": 1267,
      "ndethist": 681,
      "neargaia": 0.0941340327262878,
      "neargaiabright": -999.0,
      "nframesref": 15,
      "nid": 1333,
      "nmatches": 1972,
      "nmtchps": 8,
      "nneg": 1,
      "objectidps1": 153080502987664001,
      "objectidps2": 153090503005450064,
      "objectidps3": 153070502941218745,
      "pdiffimfilename": "ztf_20200826493796_000700_zg_c04_o_q3_scimrefdiffimg.fits",
      "pid": 1333493791415,
      "programid": 1,
      "programpi": "Kulkarni",
      "ra": 50.2987774,
      "ranr": 50.2987367,
      "rb": 0.77142858505249,
      "rbversion": "t17_f5_c3",
      "rcid": 14,
      "rfid": 700120114,
      "scorr": 6.19082307815552,
      "seeratio": 1.12769293785095,
      "sgmag1": 15.2195997238159,
      "sgmag2": -999.0,
      "sgmag3": 19.8675003051758,
      "sgscore1": 0.998749971389771,
      "sgscore2": 0.515625,
      "sgscore3": 0.896875023841858,
      "sharpnr": -0.0379999987781048,
      "sigmagap": 0.0240000002086163,
      "sigmagapbig": 0.0263000000268221,
      "sigmagnr": 0.0199999995529652,
      "sigmapsf": 0.0788011103868484,
      "simag1": 14.1837997436523,
      "simag2": 21.9748992919922,
      "simag3": 18.9829998016357,
      "sky": 0.367119193077087,
      "srmag1": 14.3689002990723,
      "srmag2": -999.0,
      "srmag3": 19.2654991149902,
      "ssdistnr": -999.0,
      "ssmagnr": -999.0,
      "ssnamenr": "null",
      "ssnrms": 208.053695678711,
      "sumrat": 1.0,
      "szmag1": 13.6730003356934,
      "szmag2": 21.0874004364014,
      "szmag3": 18.8635997772217,
      "tblid": 1,
      "tooflag": 0,
      "wall_time": "Wed, 26 Aug 2020 11:51:04 GMT",
      "xpos": 2171.86547851562,
      "ypos": 30.1760997772217,
      "zpclrcov": -6.88000000081956e-06,
      "zpmed": 25.9220008850098
   },
   "lco_id": 179910121,
   "objectId": "ZTF18aaadvkg",
   "publisher": "ZTF (www.ztf.caltech.edu)"
}


class AlertComboTestCase(TestCase):
    def setUp(self):
        temp_alert = copy.deepcopy(mars_alert)
        temp_alert['objectId'] = 'ZTF17aadevsj'
        self.mars_alert_stream = iter([mars_alert, temp_alert])
        # self.antares_alert_stream = iter([antares_alert2, antares_alert1])
        self.names = ['ZTF18aaadvkg', 'ZTF17aadevsj']

    def test_merge_mars(self):
        mars_list = list(self.mars_alert_stream)
        print(json.dumps(mars_list, indent = 3))
        merge_mars(mars_list)

        targets = list(Target.objects.all())
        for t in targets:
            print(t.name)
        for t in targets:
            self.assertIn(t.name, self.names)




        
        
