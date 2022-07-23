# -*- coding: utf-8 -*-
import datetime
import json
import scrapy
from pipelines import pre, courts, post
from pipelines.docs import be
from pipelines.exporters import as_html, fp_lzma
import src.config

class SpdrBE(scrapy.Spider):
    name = "spider_be"
    custom_settings = {
        "ITEM_PIPELINES": { 
            pre.PrePipeline: 100,
            courts.CourtsPipeline: 200,
            post.PostPipeline: 300,
            be.BEToTextPipeline: 400,
            as_html.TextToHtmlExportPipeline: 500,
            fp_lzma.FingerprintExportPipeline: 600
        }
    }

    def __init__(self, path, courts="", states="", fp=False, domains="", **kwargs):
        self.path = path
        self.courts = courts
        self.states = states
        self.fp = fp
        self.domains = domains
        self.filter = []
        if "ag" in self.courts: self.filter.append("ag")
        if "arbg" in self.courts: self.filter.append("arbg")
        if "fg" in self.courts: self.filter.append("finanzgericht")
        if "lag" in self.courts: self.filter.append("larbg")
        if "lg" in self.courts: self.filter.append("lg")
        if "lsg" in self.courts: self.filter.append("landessozialgericht")
        if "olg" in self.courts: self.filter.append("kg")
        if "ovg" in self.courts: self.filter.append("oberverwaltungsgericht")
        if "sg" in self.courts: self.filter.append("sg")
        if "vg" in self.courts: self.filter.append("vg")
        super().__init__(**kwargs)

    def start_requests(self):
        url = "https://gesetze.berlin.de/jportal/wsrest/recherche3/init"
        self.headers = src.config.be_headers
        self.cookies = src.config.be_cookies
        date = str(datetime.date.today())
        time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
        body = src.config.be_body % (date, time)
        yield scrapy.Request(url=url, method="POST", headers=self.headers, body=body, cookies=self.cookies, dont_filter=True, callback=self.parse)

    def parse(self, response):
        yield self.extract_data(response)
        url = "https://gesetze.berlin.de/jportal/wsrest/recherche3/search"
        self.headers["x-csrf-token"] = json.loads(response.body)["csrfToken"]
        date = str(datetime.date.today())
        time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
        body = '{"searchTasks":{"CATEGORY_HITS":{},"RESULT_LIST":{"start":1,"size":51,"sort":"date","addToHistory":true,"addCategory":true},"RESULT_LIST_CACHE":{"start":52,"size":50},"SEARCH_WORD_HITS":{}},"filters":{"CATEGORY":["Rechtsprechung"]},"searches":[],"clientID":"bsbe","clientVersion":"bsbe - V06_07_00 - 23.06.2022 11:20","r3ID":"s%sT%sZ"}' % (date, time)
        yield scrapy.Request(url=url, method="POST", headers=self.headers, body=body, cookies=self.cookies, meta={"batch": 50}, dont_filter=True, callback=self.parse_scrolldown)

    def parse_scrolldown(self, response):
        results = json.loads(response.body)
        if "resultList" in results:
            # Noch nicht nach ganz unten gescrollt
            yield self.extract_data(response)
            url = "https://gesetze.berlin.de/jportal/wsrest/recherche3/search"
            batch = response.meta["batch"] + 50
            date = str(datetime.date.today())
            time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
            body = '{"searchTasks":{"RESULT_LIST":{"start":%s,"size":50,"sort":"date","addToHistory":true,"addCategory":true},"RESULT_LIST_CACHE":{"start":%s,"size":50},"FAST_ACCESS":{}},"filters":{"CATEGORY":["Rechtsprechung"]},"searches":[],"clientID":"bsbe","clientVersion":"bsbe - V06_07_00 - 23.06.2022 11:20","r3ID":"%sT%sZ"}' % (batch, batch + 50, date, time)
            yield scrapy.Request(url=url, method="POST", headers=self.headers, body=body, cookies=self.cookies, meta={"batch": batch}, dont_filter=True, callback=self.parse_scrolldown)
    
    def extract_data(self, response):
        results = json.loads(response.body)
        if "resultList" in results:
            for result in results["resultList"]:
                r = {
                    "court": result["titleList"][0],
                    "date": result["date"],
                    "az": result["titleList"][1],
                    "link": "https://gesetze.berlin.de/bsbe/document/" + result["docId"],
                    "docId": result["docId"],
                    "xcsrft" : self.headers["x-csrf-token"] 
                }
                if self.filter:
                    for f in self.filter:
                        if r["court"][0:len(f)].lower() == f:
                            return r
                else:
                    return r