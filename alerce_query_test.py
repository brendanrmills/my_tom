import json, requests, logging, time
logging.basicConfig(filename = 'alerce_query_test.log',format='%(asctime)s:%(message)s',level = logging.INFO, force = True)

#this loop runs for a range of query sizes
for q_size in range(100, 1001, 50):
    #arguments define the search to the api
    args = f'page=1&page_size={q_size}&lastmjd=59097&lastmjd=59098'
    logging.info(f'Ran 2 queries with arguments {args}')

    #get response from api using arguments
    response = requests.get(f'https://api.alerce.online/ztf/v1/objects/?count=false&{args}')
    response.raise_for_status()

    #format for json and identify the object IDs
    alert_list = response.json()['items']
    namelist1 = []
    for a in alert_list:
        namelist1.append(a['oid'])

    #repeat that process
    response = requests.get(f'https://api.alerce.online/ztf/v1/objects/?count=false&{args}')
    response.raise_for_status()
    alert_list = response.json()['items']
    namelist2 = []
    for a in alert_list:
        namelist2.append(a['oid'])

    #mismatch are objects not in the same order
    #unpaired are objects that occur in one list and not the other
    mismatch = 0
    unpaired = 0
    for i in range(q_size):
        if not namelist1[i] == namelist2[i]:
            mismatch += 1
        if not namelist1[i] in namelist2:
            unpaired += 1
        if not namelist2[i] in namelist1:
            unpaired += 1
        #print(namelist1[i], namelist2[i], namelist1[i] == namelist2[i])

    print(mismatch, unpaired)
    logging.info(f'{mismatch} mismatches, {unpaired} unpaired')