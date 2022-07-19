# -*- coding: utf-8 -*-
import datetime
import requests
from lxml import html
from src.output import output

class BEToTextPipeline:
    def process_item(self, item, spider):
        # item["text"]: Berlin ist JSON-Post-Response
        url = "https://gesetze.berlin.de/jportal/wsrest/recherche3/document"
        headers = spider.headers
        headers["Referer"] = "https://gesetze.berlin.de/bsbe/document/" + item["docId"]
        date = str(datetime.date.today())
        time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
        body = '{"docId":"%s","format":"xsl","keyword":null,"sourceParams":{"source":"Unknown","category":"Alles"},"searches":[],"clientID":"bsbe","clientVersion":"bsbe - V06_07_00 - 23.06.2022 11:20","r3ID":"%sT%sZ"}' % (item["docId"], date, time)
        try:
            req = requests.post(url=url, cookies=spider.cookies, headers=headers, data=body)
        except:
            output("could not retrieve " + item["link"], "err")
        else:
            data = req.json()
            doc = html.fromstring(f'<!doctype html><html><head><title>{item["az"]}</title></head><body>{data["head"]}{data["text"]}</body></html>')
            item["text"] = html.tostring(doc, pretty_print=True, encoding="utf-8").decode("utf-8")
            item["filetype"] = "html"
            return item