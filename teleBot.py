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
updater = Updater("519012714:AAEzzClTyBV8Q3GwRZAxlJslM3mxanpcoWM")

dp=updater.dispatcher

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
        print("LOG==="+"Starting "+str(self.chat) +"'s thread, and Id is "+ str(self.threadID))
        self.kijijianMain()
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
                            print(productTitle+" is out of date.\n")
                except:
                    print("LOG==="+str(self.threadID)+"这他妈的是个广告")
            time.sleep(1800)
            #sleepRefresh(5)
        print("LOG==="+str(self.threadID)+" Thread of Kijijian has been killed clearly!")
        return

def url_maker():
    url="https://www.kijiji.ca/b-buy-sell/ottawa/"+keyword+"/k0c10l1700185?price="+minPrice+"__"+maxPrice
    return url

def sleepRefresh(sec):
    secc=sec;
    print("Refresh in "+str(sec)+" seconds")
    for i in range(101):
        sys.stdout.write('\r')
        sys.stdout.write("%s%% |%s" %(int(i%101), int(i%101)*'#'))
        sys.stdout.flush()  ##随时刷新到屏幕上
        time.sleep(5)
    print ("\n")






def kijijianStart(bot, update):
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
                print("LOG==="+"Start Thread Failed")
    except Exception as e:
        print("LOG==="+e)
    #args=(url,headers,bot,update,))
    return ConversationHandler.END

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hi")

def whoiam(bot, update):
    print("LOG==="+"whoiam")
    bot.send_message(chat_id=update.message.chat_id, text=update.message.from_user.username)
    open(update.message.from_user.photo)
    bot.send_photo(update.message.chat_id, update.message.from_user.photo)

def music(bot, update):
    print("LOG==="+"music")
    bot.sendVoice(chat_id=update.message.chat_id, voice=open("C:/Users/andy_/Downloads/test.mp3",'rb'))

def cancelk(bot, update):
    #update.message.reply_text('cancelling')
    for theThread in threads:
        if theThread.chat == update.message.chat_id:
            try:
                theThread.working=False
                threads.remove(theThread)
                bot.send_message(chat_id=update.message.chat_id, text="Kijijian is nolonger running!")
                return ConversationHandler.END
            except:
                print("LOG==="+"Failed to stop")
    update.message.reply_text('Kijijian is not running!')
    return ConversationHandler.END

def cancel(bot, update):
    #print("Ready to cancel")
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




#def inlinequery(bot, update):
#    """Handle the inline query."""
#    query = update.inline_query.query
#    results = [
#        InlineQueryResultArticle(
#            id=uuid4(),
#            title="Quo",
#            input_message_content=InputTextMessageContent("\""+query.upper()+"\""))]
#    update.inline_query.answer(results)
#
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
