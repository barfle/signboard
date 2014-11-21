from dataplicity.client.task import Task, onsignal

import math
import operator
import serial
import ystockquote
from AM03127 import AM03127

class SignboardTask(Task):
    """Runs a signboard"""

    def on_startup (self):
        self.sign = AM03127()
        self.stocks = ""

    def poll(self):
        """Called on a schedule defined in dataplicity.conf"""
        self.updateSignboard() 

    def updateSignboard (self):
        msg = self.getStockLine (self.stocks)
        self.sign.displayMessage(msg=msg, page="A", line=1, lead=self.lead, disp=self.speed, lag=self.lag, wait=self.wait, brightness="A")

    @onsignal('settings_update', 'signboard')
    def on_settings_update(self, name, settings):
        """Catches the 'settings_update' signal for 'signboard'"""
        # This signal is sent on startup and whenever settings are changed by the server
        self.brightness = settings.get('lcd', 'brightness')
        self.stocks = settings.get('lcd', 'stocks')
        self.lead = settings.get('lcd', 'lead')
        self.speed = settings.get('lcd', 'speed')
        self.lag = settings.get('lcd', 'lag')
        self.wait = settings.get('lcd', 'wait')
	self.updateSignboard()

    def getStockLine (self, stocks):
        stock_list = stocks.split()
        stockLine = ""
        for stock in stock_list:
            stockData = ystockquote.get_all(stock)
            stockLine += stock + '[' + stockData['price'] + '/' + stockData['change'] + "] "
        return stockLine
