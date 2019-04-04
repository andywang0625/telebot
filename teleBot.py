from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler,InlineQueryHandler
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import requests
import urllib,urllib3
import sys,time
from bs4 import BeautifulSoup
import threading
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4
from telegram.utils.helpers import escape_markdown
import json
import logging

FORMAT = '%(asctime)-15s - %(levelname)s - %(target)-s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger('telebot')

TITLE, MINPRICE, MAXPRICE = range(3)

POSTCANCEL=range(1)
working={}
threads = []

class kijijianThread (threading.Thread):
    def __init__(self, threadID, chat, url, header, update):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.chat = chat
        self.url = url
        self.header = header
        self.update = update
        self.list = []
        self.working=True
    def run(self):
        try:
            logger.info('Service Info: %s', "Starting "+str(self.chat) +"'s thread, and Id is "+ str(self.threadID), extra={'target':self.update.message.from_user.username})
            self.kijijianMain()
        except:
            logger.error('Service Info: %s', 'kijijian Failed to start', extra={'target':self.update.message.from_user.username})
    def kijijianMain(self):
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
                    if productTitle.find(keyword) != -1:
                        if not productDescription in self.list:
                            self.list.append(productDescription)
                            self.update.message.reply_text(productTitle+"\n"+"仅仅只卖:"+str(productPrice)+"\n"+"详情:"+productDescription+"\n"+"在"+productDate+"发售的"+"\n"+"点击查看:"+"https://www.kijiji.ca"+productUrl)
                        else:
                            logger.info('Service Info: %s', productTitle+" is Out of Date", extra={'target':self.update.message.from_user.username})
                            print(productTitle+" is out of date.\n")
                except:
                    logger.error('Service Info: %s', 'kijijian', extra={'target':self.update.message.from_user.username})
            time.sleep(1800)
            #sleepRefresh(5)
        logger.info('Thread Stoped: %s', 'Thread of Kijijian has been killed clearly!', extra={'target':self.update.message.from_user.username})
        return

def url_maker():
    url="https://www.kijiji.ca/b-buy-sell/ottawa/"+keyword+"/k0c10l1700185?price="+minPrice+"__"+maxPrice
    return url

def kijijianStart(bot, update):
    logger.info('Command Invoked: %s', "kijijian", extra={'target':self.update.message.from_user.username})
    for theThread in threads:
        if theThread.chat == update.message.chat_id:
            update.message.reply_text('You can only run one kijiji helper!')
            return
    #print("Kijijian")
    update.message.reply_text('What are you looking for?')
    return TITLE
    pass

def kijijianTitle(bot, update):
    #print(update.message.text)
    global keyword
    keyword=update.message.text
    update.message.reply_text('What is the minimum price you are looking for?')
    return MINPRICE
    pass

def kijijianMinPrice(bot, update):
    #print(update.message.text)
    global minPrice
    minPrice=update.message.text
    update.message.reply_text('What is the maximum price you are looking for?')
    return MAXPRICE
    pass;

def kijijianMaxPrice(bot, update):
    #print(update.message.text)
    global maxPrice
    maxPrice=update.message.text
    update.message.reply_text('The searching is in progress.')
    url=url_maker()
    #print("Here is the url for u:"+url)
    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'
    headers={'User-agent':user_agent}
    try:
            #print(threadID+ update.message.chat_id+ threadID+ update)
            thisThread = kijijianThread(len(threads)+1, update.message.chat_id, url, headers, update)
            #self, threadID, chat, url, header, update
            try:
                #thisThread.setDaemon(True)
                thisThread.start()
                threads.append(thisThread)
            except:
                logger.error('Command Failed: %s', 'kijijian Failed to Start -> '+str(theThread.threadID), extra={'target':update.message.from_user.username})
    except Exception as e:
        logger.error('Command Failed: %s', 'kijijian Failed to Start -> '+str(e.message), extra={'target':update.message.from_user.username})
    #args=(url,headers,bot,update,))
    return ConversationHandler.END

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hi")

def whoiam(bot, update):
    logger.info('Command Invoked: %s', 'whoiam', extra={'target':update.message.from_user.username})
    bot.send_message(chat_id=update.message.chat_id, text="@"+update.message.from_user.username)
def music(bot, update):
    logger.info('Command Invoked: %s', 'music', extra={'target':update.message.from_user.username})
    bot.sendVoice(chat_id=update.message.chat_id, voice=open("test.mp3",'rb'))

def cancelk(bot, update):
    #update.message.reply_text('cancelling')
    logger.info('Command Invoked: %s', 'cancelk', extra={'target':update.message.from_user.username})
    for theThread in threads:
        if theThread.chat == update.message.chat_id:
            try:
                theThread.working=False
                threads.remove(theThread)
                bot.send_message(chat_id=update.message.chat_id, text="Kijijian is nolonger running!")
                logger.info('Service Stoped: %s', 'cancelk -> '+str(theThread.threadID), extra={'target':update.message.from_user.username})
                return ConversationHandler.END
            except:
                logger.error('Command Failed: %s', 'cancelk is not able to stop the thread -> '+str(theThread.threadID), extra={'target':update.message.from_user.username})
    update.message.reply_text('Kijijian is not running!')
    return ConversationHandler.END

def cancel(bot, update):
    #print("Ready to cancel")
    logger.info('Command Invoked: %s', 'cancel', extra={'target':update.message.from_user.username})
    reply_keyboard = [['Kijijian','Others']]
    update.message.reply_text("Which service(s) you hope to stop?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return POSTCANCEL

def postCancel(bot, update):
    update.message.reply_text('I see!', reply_markup=ReplyKeyboardRemove())
    if update.message.text == "Kijijian":
        cancelk(bot, update)
    else:
        update.message.reply_text("No Job to Cancel!")
    return ConversationHandler.END


try:
    with open('MyApi.json', 'r') as json_file:
        data = json.load(json_file)
except:
    logger.critical('Config problem: %s', 'Not Able to Read MyApi.json', extra={'target': 'server'})
    exit()
try:
    updater = Updater(data['api'])
    dp = updater.dispatcher
    logger.info('Loding Config file: %s', 'success', extra={'target':'server'})
except:
    logger.critical('Config problem: %s','Failed to use the API', extra={'target':'server'})
    exit()
logger.info('Setting up Telebot: %s','success', extra={'target':'server'})
start_handler = CommandHandler('start', start)
whoiam_handler = CommandHandler('whoiam', whoiam)
music_handler = CommandHandler('music', music)
cancelk_handler = CommandHandler('cancelk', cancelk)
cancel_handler = ConversationHandler(
    entry_points=[CommandHandler('cancel', cancel)],
    states={
        POSTCANCEL: [MessageHandler(Filters.text, postCancel)],
    },
    fallbacks=[]
)
kijijian_handler = ConversationHandler(
    entry_points=[CommandHandler('kijijian', kijijianStart)],

    states={
        TITLE: [MessageHandler(Filters.text, kijijianTitle)],
        MINPRICE: [MessageHandler(Filters.text, kijijianMinPrice)],
        MAXPRICE: [MessageHandler(Filters.text, kijijianMaxPrice)]
    },
    fallbacks=[CommandHandler('cancelk', cancelk)]
)

dp.add_handler(start_handler)
dp.add_handler(whoiam_handler)
dp.add_handler(music_handler)
dp.add_handler(kijijian_handler)
dp.add_handler(cancelk_handler)
dp.add_handler(cancel_handler)
#dp.add_handler(InlineQueryHandler(inlinequery))

updater.start_polling()
updater.idle()
