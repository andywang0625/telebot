import requests
import urllib,urllib3
import sys,time
from bs4 import BeautifulSoup
import threading
import logging


class kijijianThread (threading.Thread):
    def __init__(self, threadID, chat, keyword, url, header, update, logger):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.chat = chat
        self.url = url
        self.header = header
        self.update = update
        self.list = []
        self.working=True
        self.logger = logger
        self.keyword = keyword
    def run(self):
        try:
            self.logger.info('Service Info: %s', "Starting "+str(self.chat) +"'s thread, and Id is "+ str(self.threadID), extra={'target':self.update.message.from_user.username})
        except e:
            self.logger.error('Service Info: %s', 'kijijian Failed to start:'+e.message, extra={'target':self.update.message.from_user.username})
        while self.working:
            response=requests.get(self.url,self.header)
            soup = BeautifulSoup(response.text,'lxml')
            #print(soup)
            productsList = soup.find_all("div",class_="info-container")
            #print(productsList)
            for product in productsList:
                soupP = BeautifulSoup(str(product),'lxml')
                productTitle=soupP.find(class_="title")
                productPricec=soupP.find(class_="price")
                productDescription=soupP.find(class_="description")
                productDate=soupP.find(class_="date-posted")
                productUrl=soupP.find(class_="title").a['href']
                try:
                    productTitle=str(productTitle.text).strip()
                    productPricec=((str((productPricec.text).strip()).replace("$","")).replace(",","")).replace(" ","")
                    productPrice=int(productPricec[0:productPricec.find(".")])
                    productDescription=str(productDescription.text).strip()
                    productDate=str(productDate.text).strip()
                    productUrl=str(productUrl).strip()
                    if productTitle.find(self.keyword) != -1:
                        if not productDescription in self.list:
                            self.list.append(productDescription)
                            self.update.message.reply_text(productTitle+"\n"+"仅仅只卖:"+str(productPrice)+"\n"+"详情:"+productDescription+"\n"+"在"+productDate+"发售的"+"\n"+"点击查看:"+"https://www.kijiji.ca"+productUrl)
                        else:
                            pass
                            #self.logger.info('Service Info: %s', productTitle+" is Out of Date", extra={'target':self.update.message.from_user.username})
                            #print(productTitle+" is out of date.\n")
                except Exception as inst:
                    self.logger.error('Service Info: %s', 'kijijian:'+inst[0], extra={'target':self.update.message.from_user.username})
            time.sleep(1800)
            #sleepRefresh(5)
        self.logger.info('Thread Stoped: %s', 'Thread of Kijijian has been killed clearly!', extra={'target':self.update.message.from_user.username})
        return
