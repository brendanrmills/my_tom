from tom_targets.models import Target
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker
from tom_alerts.brokers.alerce import ALeRCEBroker
from tom_fink.fink import FinkBroker
import json, requests, logging, time

def merge_mars(mars_alert_list):
    '''This method merges the alert list into the database target list'''
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
        print('MARS    Target', alert['objectId'], ' created'if created else ' updated!!!')
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
        print('ANTARES Target', alert['properties']['ztf_object_id'], ' created'if created else ' updated!!!')
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
        print('Fink    Target', alert["i:objectId"], ' created'if created else ' updated!!!')
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

        # get the probabilities
        url = 'https://api.alerce.online/ztf/v1/objects/'+alert['oid']+'/probabilities'
        response = requests.get(url)
        response.raise_for_status()
        probs = response.json()
        for i in range(len(probs)):
            target.save(extras = {'alerce_classification'+str(i): probs[i]})

        target.save(extras = alerce_properties)
        save_broker_extra(target, 'ALeRCE')
        print('ALeRCE  Target', alert["oid"], ' created'if created else ' updated!!!')
    logging.info(f'MergeALeRCE took {time.time()-st} sec')

def save_broker_extra(target, broker_name):
    try:
        extra = target.targetextra_set.get(key = 'broker')
        value = extra.typed_value('')
        broker_record = value.split(', ')
        if broker_name in broker_record:
            return
        target.save(extras = {'broker': extra.typed_value('') + ', ' + broker_name})
    except:
        target.save(extras = {'broker': broker_name})

def get_duplicates(targets):
    '''This function gets the targets that have been identified by multiple brokers'''
    duplicate_targets = []
    triplicate_targets = []
    for target in targets:
        broker_list = target.targetextra_set.get(key= 'broker').typed_value('').split(', ')

        if len(broker_list) ==2:
            duplicate_targets.append(target)
        if len(broker_list) == 3:
            triplicate_targets.append(target)

    return duplicate_targets, triplicate_targets
