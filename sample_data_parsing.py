from datetime import datetime
import json 
import mysql.connector
import os
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
        item['created_at'] = cre_at_date.astimezone(pytz.UTC)
        # item['created_at'] = cre_at_date.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S%z")

        if i['status'] == 'Running':
            for address_key in i['state']['network']:

              for addd_key in i['state']['network'][address_key]:
                if addd_key == 'addresses':
                    address_list = i['state']['network'][address_key][addd_key]

                    for x in address_list:
                        # append only IPv4
                        if re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", x['address']):
                            item['addresses'].append(x['address'])
                            
            item['memory_usage'] = i['state']['memory']['usage'] 
            item['cpu'] = i['state']['cpu']['usage']

        response.append(item)

mydb = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

mycursor = mydb.cursor()

for container in response:
    mycursor.execute(
        "INSERT INTO container (name, status, created_at_utc, addresses, cpu, memory_usage) VALUES (%s, %s, %s, %s, %s, %s)", 
        (container['name'], 
        container['status'], 
        container['created_at'].strftime("%Y-%m-%d %H:%M:%z"),
        ', '.join(container['addresses']),
        container['cpu'],
        container['memory_usage'],
        ))
    mydb.commit()
