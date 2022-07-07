from tom_targets.models import Target, TargetList
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker
from tom_alerts.brokers.alerce import ALeRCEBroker
from tom_fink.fink import FinkBroker
from classifications.models import TargetClassification
from astropy.time import Time
import json, requests, logging, time
from urllib.parse import urlencode

def merge_mars(mars_alert_list):
    '''This method merges the alert list into the database target list
    It firstts gets_or_creates the target object
    then it assembles a dictionary of soon-to-be targetextras with proper naming
    it saves the target extras and the broker tag'''
    st = time.time()
    for alert in mars_alert_list:
        try: #create target
            created = False
            target = Target.objects.get(name = alert['objectId'])
        except:
            target = MARSBroker().to_target(alert)
            created = True

        #rename the dictionaty
        mars_properties = {}
        for k in alert['candidate'].keys():
            mars_properties['mars_' + k] = alert['candidate'][k]
        
        #add the target extra data
        target.save(extras = mars_properties)
        save_broker_extra(target, 'MARS')
        # print statement
        # print('MARS    Target', alert['objectId'], ' created'if created else ' updated!!!')
    logging.info(f'MergeMARS took {time.time()-st} sec')

def merge_antares(antares_alert_list):
    st = time.time()
    for alert in antares_alert_list:
        try: #create target
            created = False
            target = Target.objects.get(name = alert['properties']['ztf_object_id'])
        except:
            target,_,_ = ANTARESBroker().to_target(alert)
            created = True
        #redefines the keys of the alert to be preceded by "antares_"
        antares_properties = {}
        for k in alert['properties'].keys():
            antares_properties[f'antares_{k}'] = alert['properties'][k]

        target.save(extras = antares_properties)
        target.save(extras = {'antares_tags': alert['tags']})
        save_broker_extra(target, 'ANTARES')
        # print('ANTARES Target', alert['properties']['ztf_object_id'], ' created'if created else ' updated!!!')
    logging.info(f'MergeANTARES took {time.time()-st} sec')

def merge_fink(fink_alert_list):
    st = time.time()
    for alert in fink_alert_list:
        try: #create target
            created = False
            target = Target.objects.get(name = alert["i:objectId"])
        except:
            target = FinkBroker().to_target(FinkBroker().to_generic_alert(alert))
            created = True
        #redefines the keys of the alert to be preceded by "antares_"
        fink_properties = {}
        for k in alert.keys():
            fink_properties['fink_{}'.format(k)] = alert[k]

        target.save(extras = fink_properties)
        save_broker_extra(target, 'Fink')

        #deal with fink classification
        classif = target.targetextra_set.get(key = 'fink_v:classification').typed_value('')
        mjd = target.targetextra_set.get(key = 'fink_i:jd').typed_value('number') - 2400000
        save_target_classification(target, 'Fink', '', classif, 0.0, mjd)

        # print('Fink    Target', alert["i:objectId"], ' created'if created else ' updated!!!')
    logging.info(f'MergeFink took {time.time()-st} sec')

def merge_alerce(alerce_alert_list):
    st = time.time()
    for alert in alerce_alert_list:
        try: #create target
            created = False
            target = Target.objects.get(name = alert["oid"])
        except:
            target = ALeRCEBroker().to_target(alert)
            created = True
        #redefines the keys of the alert to be preceded by "antares_"
        alerce_properties = {}
        for k in alert.keys():
            alerce_properties['alerce_{}'.format(k)] = alert[k]

        #save the targetExtra data
        target.save(extras = alerce_properties)
        save_broker_extra(target, 'ALeRCE')

        # get the probabilities
        url = 'https://api.alerce.online/ztf/v1/objects/'+alert['oid']+'/probabilities'
        response = requests.get(url)
        response.raise_for_status()
        probs = response.json()
        alerce_probs(target, probs)
        
        #print('ALeRCE  Target', alert["oid"], ' created'if created else ' updated!!!')
    logging.info(f'MergeALeRCE took {time.time()-st} sec')

def merge_lasair(lasair_alert_list):
    st = time.time()
    for alert in lasair_alert_list:
        try: #create target
            created = False
            target = Target.objects.get(name = alert["objectId"])
        except:
            target = Target.objects.create(
            name=alert.get('objectId'),
            type='SIDEREAL',
            ra=alert.get('ramean'),
            dec=alert.get('decmean'),
            )
            created = True
        save_broker_extra(target, 'Lasair')
        save_target_classification(target, 'Lasair', '', alert['classification'], alert['classificationReliability'], alert['jdmax'] - 2400000)
        #there is not target estra data saved for these
        # print('Lasair  Target', alert["objectId"], ' created'if created else ' updated!!!')

    logging.info(f'MergeLasair took {time.time()-st} sec')

def save_broker_extra(target, broker_name):
    '''This method saves the broker as a target extra and appends the target to the targetlist for that broker'''
    tl, _ = TargetList.objects.get_or_create(name = broker_name)
    tl.targets.add(target)
    try:
        extra = target.targetextra_set.get(key = 'broker')
        value = extra.typed_value('')
        broker_record = value.split(', ')
        if broker_name in broker_record:
            return #Watch out!! there is a return here
        target.save(extras = {'broker': extra.typed_value('') + ', ' + broker_name})
    except:
        target.save(extras = {'broker': broker_name})
    

def save_target_classification(target, broker, level, classif, prob, mjd):
    '''This method gets or creates a classification object that matches the values passed to the method
    it returns the classification'''
    c,_ = TargetClassification.objects.get_or_create(target = target, source = broker, level = level, classification = classif, probability = prob, mjd = mjd)
    c.save()
    return c

def alerce_probs(target, probs):
    '''This method handles the classification probability of the alerce classicication. It takes the json object
    and saves it as a target_classification. It has a built in Unknown classification if there is no data given'''
    mjd = target.targetextra_set.get(key = 'alerce_lastmjd').typed_value('number')
    if probs:
        for p in probs:
            if p['classifier_version'] =="stamp_classifier_1.0.4":
                pass
                #save_target_classification(target, 'ALeRCE*', p['classifier_name'] + '*', p['class_name'] + '*', p['probability'], mjd)
            else:
                save_target_classification(target, 'ALeRCE', p['classifier_name'], p['class_name'], p['probability'], mjd)
    else:
        save_target_classification(target, 'ALeRCE', '', 'Unknown', 0.0, mjd)

def get_duplicates(targets):
    '''This function gets the targets that have been identified by multiple brokers'''
    duplicate_targets = []
    triplicate_targets = []
    quads = []
    for target in targets:
        # print(target.name)
        broker_list = target.targetextra_set.get(key= 'broker').typed_value('').split(', ')

        if len(broker_list) ==2:
            duplicate_targets.append(target)
        if len(broker_list) == 3:
            triplicate_targets.append(target)
        if len(broker_list) == 4:
            quads.append(target)
        

    return duplicate_targets, triplicate_targets, quads

# These methods are for running in find_unknowns
def clean_duplicate_classifs():
    '''This method goes through all the targets and the assiciated target classifications,
    and if a target has a duplicate classification it will delete the duplicate.'''

    logging.info('Start: cleaning duplicate classifications')
    st= time.time()
    targets = list(Target.objects.all())
    dups = 0
    for t in targets:
        tcs = TargetClassification.objects.filter(target = t)
        tc_dicts = [tc.as_dict() for tc in tcs]
        for tc in tcs:
            if tc_dicts.count(tc.as_dict()) > 1:
                dups += 1
                tc.delete()
                tcs = TargetClassification.objects.filter(target = t)
                tc_dicts = [tc.as_dict() for tc in tcs]
    logging.info(f'Done: cleaning {dups} duplicate classifications, it took {time.time()- st} sec')
    return dups

def register_duplicates():
    '''This method goes through the list of targets and adds them to TargetList objects
    based on whether they are covered by multiple alerts. It also specially picls out 
    targets with both ALeRCE and Fink'''
    logging.info('Start: register duplicates')
    st = time.time()
    targets = Target.objects.all()
    dups, _  = TargetList.objects.get_or_create(name = 'Duplicates')
    trips, _ = TargetList.objects.get_or_create(name = 'Triplicates')
    alfin, _ = TargetList.objects.get_or_create(name = 'ALeRCE + Fink')
    alfinlas, _ = TargetList.objects.get_or_create(name = 'Alerce + Fink + Lasair')

    dups_len = len(dups.targets.all())
    trips_len = len(trips.targets.all())
    alfin_len = len(alfin.targets.all())
    alfinlas_len = len(alfinlas.targets.all())

    for t in targets:
        broker_extra = t.targetextra_set.get(key = 'broker')
        brokers = broker_extra.typed_value('').split(', ')
        if len(brokers) == 2:
            dups.targets.add(t)
        if len(brokers) == 3:
            trips.targets.add(t)
        if 'Fink' in brokers and 'ALeRCE' in brokers:
            alfin.targets.add(t)
        if 'Fink' in brokers and 'ALeRCE' in brokers and 'Lasair' in brokers:
            alfinlas.targets.add(t)
    dups_len2 = len(dups.targets.all())
    trips_len2 = len(trips.targets.all())
    alfin_len2 = len(alfin.targets.all())
    alfinlas_len2 = len(alfinlas.targets.all())
    logging.info(f'Done: register duplicates, got {dups_len2 - dups_len} dups, {trips_len2 - trips_len} trips, {alfin_len2 - alfin_len} alfins, and {alfinlas_len2-alfinlas_len} Alfinlas')
    logging.info(f'    It took {time.time() - st} sec')
    logging.info(f'    There are now {dups_len2} duplicates, {trips_len2} triplicates, {alfin_len2} Alfins, and {alfinlas_len2} in Alfinlas')

def find_unknowns():
    '''This method loops through all the targets and finds the ones that do not have classifications or are classified only as unknown'''
    logging.info('Start: finding unknowns')
    targets = Target.objects.all()
    no_classif = 0
    unks = 0
    for t in targets:
        tcs = t.targetclassification_set.all()
        if len(tcs) == 0:
            no_classif += 1
        
        if len(tcs) == 1 and tcs[0].classification == 'Unknown':
            unks += 1
    logging.info(f'Done: there are {unks} unknowns and {no_classif} without any classifications')
    return unks, no_classif