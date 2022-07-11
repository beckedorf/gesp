# -*- coding: utf-8 -*-
import datetime
import re
import requests
from lxml import html
from output import output

class HEPipeline:
    def process_item(self, item, spider):
        # Senate / Kammern / Einzelrichter abschneiden 
        item["court"] = re.split(r"([-]?\d+)", item["court"])[0]
        #  Eigennamen entfernen
        names = ["hessischer-", "hessisches-", "-abteilung"]
        for name in names:
                if name in item["court"]:
                    item["court"] = item["court"].replace(name, "")
        # Gerichtstypen abkürzen
        courts = {"finanzgericht": "fg", "landesarbeitsgericht": "lag", "landessozialgericht": "lsg", "verwaltungsgerichtshof": "vgh" }
        for key in courts:
            if key in item["court"]:
                item["court"] = item["court"].replace(key, courts[key])
        # item["text"]: Hessen ist JSON-Post-Response
        url = "https://www.lareda.hessenrecht.hessen.de/jportal/wsrest/recherche3/document"
        headers = spider.headers
        headers["Referer"] = "https://www.lareda.hessenrecht.hessen.de/bshe/document/" + item["docId"]
        date = str(datetime.date.today())
        time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
        body = '{"docId":"%s","format":"xsl","keyword":null,"docPart":"L","sourceParams":{"source":"TL","position":1,"sort":"date","category":"Rechtsprechung"},"searches":[],"clientID":"bshe","clientVersion":"bshe - V06_07_00 - 23.06.2022 11:20","r3ID":"%sT%sZ"}' % (item["docId"], date, time)
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