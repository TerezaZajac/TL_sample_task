import json 
from datetime import datetime
import pytz
import re

# Parsing přiložených dat: seznam lxc kontejnerů na testovacím serveru ve formátu JSON, výstupem pro každý kontejner: name, cpu a memory usage, created_at, status a všechny přiřazené IP adresy.

response = []
with open('./sample-data.json') as json_file:
    data = json.load(json_file)

    for i in data:
        item = {}
        item['name'] = i['name']
        item['status'] = i['status']
        item['addresses'] = []
        item['cpu'] = None
        item['memory_usage'] = None
        
#convert datetime to UTC timestamp      
        cre_at_date = datetime.strptime(i['created_at'], "%Y-%m-%dT%H:%M:%S%z")

        item['created_at'] = cre_at_date.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S%z")
        
        # print ("")
        # print(i['name'])

        if i['status'] == 'Running':
            for address_key in i['state']['network']:

              for addd_key in i['state']['network'][address_key]:
                if addd_key == 'addresses':
                    address_list = i['state']['network'][address_key][addd_key]

                    for x in address_list:
                        if re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", x['address']):
                            item['addresses'].append(x['address'])
                            
            item['memory_usage'] = i['state']['memory']['usage'] 
            item['cpu'] = i['state']['cpu']['usage']
        response.append(item)


print(response)
