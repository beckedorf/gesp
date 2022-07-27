# -*- coding: utf-8 -*-
import datetime
import json
import lzma
import os
import requests
import src.config
from src.output import output
from src.get_text import bb, be, bw, by, he, hh, mv, ni, nw, rp, sh, sl, sn, st, th
from src.create_file import save_as_html, save_as_pdf

class Fingerprint:
    items = []
    input = ""
    def __init__(self, path, fp_path):
        self.load_file(fp_path)        
        for i in self.items[1:]: # Erste Zeile enthält noch keine Entscheidung
            # Ordner erstellen
            if (not os.path.exists(path + i["s"])):
                try:
                    os.makedirs(path + i["s"])
                except:
                    output("could not create folder %s%s" % (path, i["s"]), "err")
            # Umwandeln in item-Format
            item = { "court": i["c"], "date": i["d"], "az": i["az"] }
            if "link" in i:
                item["link"] = i["link"]
            if "docId" in i: # JSON-Post (BE, HH, ....)
                item["docId"] = i["docId"]
            if "body" in item: # Sachsen (zum Teil)
                item["body"] = i["body"]
            # Wenn keine To-Text-Umwandlung notwendig ist: Entscheidung herunterladen
            if i["s"] == "bund":
                save_as_html(item, i["s"], path)
            elif i["s"] in ["hb", "sn"]:
                save_as_pdf(item, i["s"], path)
            # Ansonsten: Bei JSON-Portalen zunächst x-csrf-Token in die Header einfügen (Teil der Spider)
            # & bei allen: an get_text-Funktionen weiterleiten
            else:
                date = str(datetime.date.today())
                time = str(datetime.datetime.now(datetime.timezone.utc).time())[0:-3]
                if i["s"] == "bb":
                    item = bb(item)
                elif i["s"]  == "be":
                    url = "https://gesetze.berlin.de/jportal/wsrest/recherche3/init"
                    headers = src.config.be_headers
                    body = src.config.be_body % (date, time)
                    try:
                        response = requests.post(url=url, headers=headers, cookies=src.config.be_cookies, data=body)
                    except:
                        output("be: could not get x-csrf-token", "err")
                    else:
                        headers["x-csrf-token"] = json.loads(response.body)["csrfToken"]
                    item = be(item, headers, src.config.be_cookies)
                elif i["s"] == "bw":
                    item = bw(item)
                elif i["s"] == "by":
                    item = by(item)
                elif i["s"]  == "he":
                    url = "https://www.lareda.hessenrecht.hessen.de/jportal/wsrest/recherche3/init"
                    headers = src.config.he_headers
                    body = src.config.he_body % (date, time)
                    try:
                        response = requests.post(url=url, headers=headers, cookies=src.config.he_cookies, data=body)
                    except:
                        output("he: could not get x-csrf-token", "err")
                    else:
                        headers["x-csrf-token"] = json.loads(response.body)["csrfToken"]
                    item = he(item, headers, src.config.he_cookies)
                elif i["s"]  == "hh":
                    url = "https://www.landesrecht-hamburg.de/jportal/wsrest/recherche3/init"
                    headers = src.config.hh_headers
                    body = src.config.hh_body % (date, time)
                    try:
                        response = requests.post(url=url, headers=headers, cookies=src.config.hh_cookies, data=body)
                    except:
                        output("hh: could not get x-csrf-token", "err")
                    else:
                        headers["x-csrf-token"] = json.loads(response.body)["csrfToken"]
                    item = hh(item, headers, src.config.hh_cookies)
                elif i["s"]  == "mv":
                    url = "https://www.landesrecht-mv.de/jportal/wsrest/recherche3/init"
                    headers = src.config.mv_headers
                    body = src.config.mv_body % (date, time)
                    try:
                        response = requests.post(url=url, headers=headers, cookies=src.config.mv_cookies, data=body)
                    except:
                        output("mv: could not get x-csrf-token", "err")
                    else:
                        headers["x-csrf-token"] = json.loads(response.body)["csrfToken"]
                    item = mv(item, headers, src.config.mv_cookies)
                elif i["s"] == "ni":
                    item = ni(item)
                elif i["s"] == "nw":
                    item = nw(item)
                elif i["s"]  == "rp":
                    url = "https://www.landesrecht.rlp.de/jportal/wsrest/recherche3/init"
                    headers = src.config.rp_headers
                    body = src.config.rp_body % (date, time)
                    try:
                        response = requests.post(url=url, headers=headers, cookies=src.config.rp_cookies, data=body)
                    except:
                        output("rp: could not get x-csrf-token", "err")
                    else:
                        headers["x-csrf-token"] = json.loads(response.body)["csrfToken"]
                    item = rp(item, headers, src.config.rp_cookies)
                elif i["s"]  == "sh":
                    item = sh(item)
                elif i["s"]  == "sl":
                    url = "https://recht.saarland.de/jportal/wsrest/recherche3/init"
                    headers = src.config.sl_headers
                    body = src.config.sl_body % (date, time)
                    try:
                        response = requests.post(url=url, headers=headers, cookies=src.config.sl_cookies, data=body)
                    except:
                        output("sl: could not get x-csrf-token", "err")
                    else:
                        headers["x-csrf-token"] = json.loads(response.body)["csrfToken"]
                    item = sl(item, headers, src.config.sl_cookies)
                elif i["s"]  == "sn":
                    a = 1 # Platzhalter
                    # TO-DO!
                elif i["s"]  == "st":
                    url = "https://www.landesrecht.sachsen-anhalt.de/jportal/wsrest/recherche3/init"
                    headers = src.config.st_headers
                    body = src.config.st_body % (date, time)
                    try:
                        response = requests.post(url=url, headers=headers, cookies=src.config.st_cookies, data=body)
                    except:
                        output("st: could not get x-csrf-token", "err")
                    else:
                        headers["x-csrf-token"] = json.loads(response.body)["csrfToken"]
                    item = st(item, headers, src.config.st_cookies)
                elif i["s"]  == "th":
                    url = "https://landesrecht.thueringen.de/jportal/wsrest/recherche3/init"
                    headers = src.config.th_headers
                    body = src.config.th_body % (date, time)
                    try:
                        response = requests.post(url=url, headers=headers, cookies=src.config.th_cookies, data=body)
                    except:
                        output("th: could not get x-csrf-token", "err")
                    else:
                        headers["x-csrf-token"] = json.loads(response.body)["csrfToken"]
                    item = th(item, headers, src.config.th_cookies)
                save_as_html(item, i["s"], path)
        
    def load_file(self, fp):
        lzmad = lzma.LZMADecompressor()
        with open(fp, "rb") as f:
            while chunk := f.read(1024):
                r = lzmad.decompress(chunk) # compressed -> decompressed
                r = r.decode() # bytes -> string (json)
                self.to_item(r)
        
    def to_item(self, chunk_as_str):
        self.input = self.input + chunk_as_str
        json_lines = self.input.split("|")
        if json_lines[1]:
            for line in json_lines[:-1]:
                self.items.append(json.loads(line)) # string (json) -> item (dict)
            if not json_lines[-1] == "":
                self.input = json_lines[-1] # Rest an Input anhängen
        elif json_lines[0] != "":
            self.items.append(json.loads(json_lines[0]))

#    def __init__(self, version, args, path):
#        self.nr = 0
#        self.lzmac = lzma.LZMACompressor()
#        self.path = path + "fingerprint.json"
#        self.file = open(self.path, "w")
#        general_info = '{"version":"%s","args":{"c":"%s","s":"%s"}' % (version, args["c"], args["p"])
#        self.file.write(self.lzmac.compress(general_info))
#
#    def __enter__(self):
#        return self
#
#    def add(self, state, item):
#        if "link" in item:
#            data = '"%s"' % (item["link"])
#        else:
#            data = '"%s"' % (item["link"])
#        entry = json.dumps(',"%s":{"c":"%s","d":"%s","a":"%s","f":%s}' % (self.nr, item["court"], item["date"], item["az"], data))
#        self.file.write(self.lzmac.compress(entry))
#        self.nr += 1
#
#    def __exit__(self, exc_type, exc_value, traceback):
#        self.file.write(self.lzmac.compress("}"))
#        self.file.write(self.lzmac.flush())
#        self.file.close()