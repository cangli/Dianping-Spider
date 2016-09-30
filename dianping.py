# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import logging
from requests.exceptions import HTTPError, ConnectionError
import openpyxl
import copy
import collections
import random
import time
from urllib.parse import urljoin


class dianpSpider():
    def __init__(self):
        self.headers = {
            "Host": "www.dianping.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.starturl = "http://www.dianping.com/search/category/4/10/g103/p1"
        self.page = 1
        self.infoList = []
        self.kindurl = collections.OrderedDict()
        self.kindDict = {}

    def getKind(self, se):
        re = se.get(self.starturl, headers=self.headers)
        soup = BeautifulSoup(re.text, "lxml")
        kindList = soup.select("div#classfy a")
        for k in kindList:
            self.kindurl[k.text] = urljoin(self.starturl, k["href"])

    def setLog(self):
        logger = logging.getLogger("dianping spider")
        formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
        file_handler = logging.FileHandler("D:\\dianpingsp.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    def ParsePage(self, re):
        soup = BeautifulSoup(re.text, "lxml")
        shopList = soup.select("div#shop-all-list ul li.")
        for shop in shopList:
            shopDict = collections.OrderedDict()
            name = shop.find("h4").text
            # if name in self.nameList:
            #     continue
            shopDict["name"] = name
            # self.nameList.append(name)
            shopDict["address"] = shop.select("span.addr")[0].text
            try:
                shopDict["rank-star"] = shop.select("span.sml-rank-stars")[0]["title"]
            except:
                shopDict["rank-star"] = ""
            try:
                shopDict["comment-num"] = int(shop.select("a.review-num b")[0].text)
            except:
                shopDict["comment-num"] = 0
            try:
                shopDict["mean-price"] = shop.select("a.mean-price b")[0].text
            except:
                shopDict["mean-price"] = ""
            try:
                shopDict["flavor"] = float(shop.select("span.comment-list span b")[0].text)
            except:
                shopDict["flavor"] = 0
            try:
                shopDict["environment"] = float(shop.select("span.comment-list span b")[1].text)
            except:
                shopDict["environment"] = 0
            try:
                shopDict["service"] = float(shop.select("span.comment-list span b")[2].text)
            except:
                shopDict["service"] = 0
            self.infoList.append(copy.deepcopy(shopDict))
        print("finish page{!s}".format(self.page))
        try:
            nextpage = soup.select("div.page a.next")[0]["href"]
        except:
            return None
        url = urljoin(self.starturl, nextpage)
        self.page += 1
        return url

    def makeRequest(self, se, url):
        self.page = 1
        while True:
            time.sleep(2 + random.random())
            for i in range(3):
                try:
                    re = se.get(url, headers=self.headers)
                    if re.status_code == 200:
                        break
                except HTTPError as e:
                    logging.info("HTTPError happened:{!s}".format(e))
                    logging.info("failed request the {!s} page the {!s} time".format(self.page, i))
                except ConnectionError as e:
                    logging.info("ConnectionError happened:{!s}".format(e))
                    logging.info("failed request the {!s} page the {!s} time".format(self.page, i))
                except Exception as e:
                    logging.info("Some strange error happened:{!s}".format(e))
                    logging.info("failed request the {!s} page the {!s} time".format(self.page, i))
            else:
                logging.error("failed request the {!s} page".format(self.page))
            url = self.ParsePage(re)
            if url is None:
                break

    def saveExcel(self):
        wb = openpyxl.Workbook()
        for k, v in self.kindDict.items():
            ws = wb.create_sheet(k)
            ws.append(list(v[0].keys()))
            for info_dict in v:
                ws.append(list(info_dict.values()))
        wb.save("dianping_gz.xlsx")

    def runSpider(self):
        self.setLog()
        se = requests.Session()
        self.getKind(se)
        for name, url in self.kindurl.items():
            print("start scraping {!s}".format(url))
            self.makeRequest(se, url)
            self.kindDict[name] = self.infoList
            self.infoList = []
        self.saveExcel()

if __name__ == '__main__':
    sp = dianpSpider()
    sp.runSpider()
