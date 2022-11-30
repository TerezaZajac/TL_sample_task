from datetime import datetime
import bspump
import bspump.common
import bspump.file
import bspump.mysql
import bspump.trigger
import re
import pytz
import logging

import traceback


L = logging.getLogger(__name__)

# Parsing přiložených dat: seznam lxc kontejnerů na testovacím serveru ve formátu JSON, výstupem pro každý kontejner: name, cpu a memory usage, created_at, status a všechny přiřazené IP adresy.


class ListItemGenerator(bspump.Generator):
    async def generate(self, context, event, depth):
        for i in event:

            item = {}
            item['name'] = i['name']
            item['status'] = i['status']
            item['addresses'] = []
            item['cpu'] = None
            item['memory_usage'] = None

            #convert datetime to UTC timestamp
            cre_at_date = datetime.strptime(i['created_at'], "%Y-%m-%dT%H:%M:%S%z")
            item['created_at'] = cre_at_date.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")


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
            
            item['addresses'] = ', '.join(item['addresses'])

            self.Pipeline.inject(context, item, depth)



class JSONPipeline(bspump.Pipeline):

    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)


        self.Sink = bspump.mysql.MySQLSink(app, self, "MySQLConnection", config={
            'query': "INSERT INTO container (name, status, created_at_utc, addresses, cpu, memory_usage) VALUES (%s, %s, %s, %s, %s, %s);", 
            'data': 'name,status,created_at,addresses,cpu,memory_usage'
        })

        self.build(
            bspump.file.FileJSONSource(
                app,
                self,
                config={
                    "path": "./sample-data.json",
                    "post": "noop",
                },
            ).on(bspump.trigger.RunOnceTrigger(app)),
            ListItemGenerator(app, self),
            bspump.common.DictToJsonBytesParser(app, self),
            # bspump.common.CySimdJsonParser(app, self),
          
            # bspump.common.PPrintSink(app, self),
            self.Sink,
        )


if __name__ == "__main__":
    app = bspump.BSPumpApplication()

    svc = app.get_service("bspump.PumpService")
    svc.add_connection(bspump.mysql.MySQLConnection(app, "MySQLConnection"))
    
    pl = JSONPipeline(app, "JSONPipeline")

    svc.add_pipeline(pl)
    pl.PubSub.publish("go!")
    app.run()
