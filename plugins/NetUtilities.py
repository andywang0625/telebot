from pythonping import ping
import os
import json
from pathlib import Path

class NetUtilities(object):
    def __init__(self, logger):
        self.logger = logger
        with open(r"config/MyServices.json", 'r') as json_file:
            self.services = json.load(json_file)
        try:
            with open(r"config/MyServices.json", 'r') as json_file:
                self.services = json.load(json_file)
        except:
            self.logger.error('Config problem: %s', 'Not Able to Read MyServices.json', extra={'target': 'serviceStatus'})
    def pingHost(self, bot, update, args):
        self.logger.info('Service Info: %s', "Starting NetUtilities-pingHost => "+str(args), extra={'target':update.message.from_user.username})
        for host in args:
            try:
                update.message.reply_text(str(ping(host)))
            except:
                update.message.reply_text("Error:ping => "+host)
                self.logger.error('Service Error: %s', 'Ping: => '+host, extra={'target': 'serviceStatus'})
    def serviceStatus(self, update):
        self.logger.info('Service Info: %s', "Starting NetUtilities-serviceStatus", extra={'target':update.message.from_user.username})
        for theService in self.services["Services"]:
            try:
                update.message.reply_text(theService["name"]+"-"+str(ping(theService["url"])))
            except:
                update.message.reply_text("Error:ping => "+theService)
                self.logger.error('Service Error: %s', 'Service Status: => '+theService, extra={'target': 'serviceStatus'})
