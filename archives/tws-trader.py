#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# This script is an exmple of using the (optional) ib.opt package
# instead of the regular API.
##

from ib.opt import ibConnection, message
from ib.ext.Contract import Contract
from ib.ext.ExecutionFilter import ExecutionFilter
from ib.ext.Order import Order
from random import randint
from time import sleep
import datetime
import re
import string
import sys
import time
import urllib
import yaml

ORDERS = []
EXECUTIONS = {}
global SNOOZE

class DataHandler:
    def loadOffsetExecutions(self):
        offsetExecutions = {}
        try:
            f = open('offsetExecutions.yaml', 'r')
            temp = yaml.safe_load(f)
            f.close()
            offsetExecutions = temp
            return offsetExecutions
        except Exception as e:
            print "FATAL ERROR: Need to be able to open offset executions records!"
            print "If this is a new run of the bot, try creating offsetExecutions.yaml with a yaml dictionary"
    def saveOffsetExecutions(self, executions):
        f = file('offsetExecutions.yaml', 'w')
        yaml.dump(executions, f, default_flow_style=False)
        
class Parameters:
    bid = 0
    ask = 0
    def spread(self):
        f = open('parameters.yaml', 'r')
        temp = yaml.safe_load(f)
        f.close()
        return temp["spread"]
    def floor(self):
        f = open('parameters.yaml', 'r')
        temp = yaml.safe_load(f)
        f.close()
        return float(temp["floor"])
    def step(self):
        f = open('parameters.yaml', 'r')
        temp = yaml.safe_load(f)
        f.close()
        return float(temp["step"])
    def symbol(self):
        return "SLV"
    def qty(self):
        f = open('parameters.yaml', 'r')
        temp = yaml.safe_load(f)
        f.close()
        return int(temp["qty"])
    def ceiling(self):
        #data = []
        #url = 'http://finance.yahoo.com/d/quotes.csv?s='
        #for s in 'slv'.split():
        #    url += s+"+"
        #url = url[0:-1]
        #url += "&f=sb3b2l1l"
        #f = urllib.urlopen(url,proxies = {})
        #rows = f.readlines()
        #for r in rows:
        #    values = [x for x in r.split(',')]
        #    symbol = values[0][1:-1]
        #    bid = float(values[1])
        #    ask = float(values[2])
        #    last = float(values[3])
        #    data.append({"symbol":symbol,"bid":bid,"ask":ask,"last":last,"time":values[4]})
        ##return data[0] # might change this for multi-symbol support, eventually
        #
        ## Market sell price is literal ceiling
        #ceiling = data[0]["ask"]

        if self.bid <= 0:
            return 0
        else:
            ceiling = self.bid

            # Gap lower so market has to drop before we buy anything
            gap = self.spread() * 0.90
            ceiling = ceiling - gap

            return ceiling

dataHandler = DataHandler()
parameters = Parameters()

def my_account_handler(msg):
    print msg

lastWriteSize = 0
def my_tick_handler(msg):
    global parameters
    global lastWriteSize
    if hasattr(msg, "price"):
        # 1 = bid
        # 2 = ask
        # 4 = last
        # 6 = high
        # 7 = low
        # 9 = close

        priceLog = {}
        date = datetime.date.today()
        priceLogFile = "%s.yaml" % date.strftime("%Y-%m-%d")
        try:
            f = open(priceLogFile, 'r')
            temp = yaml.safe_load(f)
            f.close()
            priceLog = temp
        except Exception as e:
            pass

        side = ""
        if msg.field == 2:
            sys.stdout.write("a%0.2f " % msg.price)
            if msg.price > parameters.ask:
                insertBids()
            parameters.ask = msg.price
            side = "ask"
        elif msg.field == 1:
            sys.stdout.write("b%0.2f " % msg.price)
            parameters.bid = msg.price
            side = "bid"
        if side != "":
            priceLog[time.time()] = [side, msg.price]

            sys.stdout.flush()
            if len(priceLog) % 10 == 0:
                print " "
            
            f = open(priceLogFile, "w" )
            yaml.dump(priceLog, f) #, default_flow_style=False)
            f.close()

def my_openorder_handler(msg):
    global ORDERS
    global SNOOZE
    orderId = msg.orderId
    orderState = msg.orderState
    order = {}
    order["orderId"] = msg.order.m_orderId
    order["symbol"] = msg.contract.m_symbol
    order["qty"] = msg.order.m_totalQuantity
    order["price"] = msg.order.m_lmtPrice
    order["action"] = msg.order.m_action
    print "--> Open order: %s" % order
    print "Status: %s Warning: %s" % (orderState.m_status, orderState.m_warningText)
    ORDERS.append(order)
    SNOOZE = time.time() + 0.5

def execDetails(msg):
    #global EXECUTIONS
    global dataHandler
    global parameters
    global con
    order = {}
    order["orderId"] = msg.orderId
    order["symbol"] = msg.contract.m_symbol
    order["side"] = msg.execution.m_side
    order["qty"] = msg.execution.m_shares
    order["price"] = msg.execution.m_price
    dateblocks = re.split(' +', msg.execution.m_time)
    year = int(dateblocks[0][0:4])
    month = int(dateblocks[0][4:6])
    day = int(dateblocks[0][6:8])
    time = re.split(':', dateblocks[1])
    dt = datetime.datetime(year, month, day, int(time[0]), int(time[1]), int(time[2]))
    order["time"] = dt
    execId = msg.execution.m_execId
    order["execId"] = execId

    print "--> Executed order: %s" % order

    executions = dataHandler.loadOffsetExecutions()
    if not execId in executions:
        executions[execId] = order

        if order["side"] == "BOT":
            spread = parameters.spread()
            qty = order["qty"]
            symbol = parameters.symbol()
            price = order["price"] + spread
            newOrder = make_order(qty, price, 'SELL')
            newContract = make_contract(symbol)
            print "--> execDetails: %i shares bought at %f (#%s), selling at %f" % (qty, order["price"], order["orderId"], price)
            print "--> PLACING ASK: qty %i price %i" % (qty, price)
            con.placeOrder(id=next_order_id(), contract=newContract, order=newOrder)

        dataHandler.saveOffsetExecutions(executions)
        

order_ids = [0]
initialized = 0
def save_order_id(msg):
    global initialized
    order_ids.append(msg.orderId)
    initialized = 1
def next_order_id():
    order_id = order_ids[-1]
    order_ids.append(order_id+1)
    return order_id

def error_handler(msg):
    if msg.errorCode == 502:
        print "--> TWS NOT RUNNING OR NOT READY FOR CONNECTION!  EXITING!"
        sys.exit(1)
    elif msg.errorCode == 2104:
        print "--> %s" % msg.errorMsg
    else:
        print msg

def gen_tick_id():
    i = randint(100, 10000)
    while True:
        yield i
        i += 1
gen_tick_id = gen_tick_id().next
generic_tick_keys = '100,101,104,106,162,165,221,225,236'

def make_contract(symbol):
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = 'STK'
    contract.m_exchange = 'SMART'
    contract.m_primaryExch = 'SMART'
    contract.m_currency = 'USD'
    contract.m_localSymbol = symbol
    return contract

def make_order(qty, limit_price, action):
    order = Order()
    order.m_minQty = qty
    order.m_lmtPrice = limit_price
    order.m_orderType = 'LMT'
    order.m_totalQuantity = qty
    order.m_action = action
    order.m_tif = 'GTC'
    order.m_outsideRth = True
    return order

def insertBids():
    ### Place buy orders
    global ORDERS
    floor = parameters.floor()
    ceiling = parameters.ceiling()
    if ceiling == 0:
        print "--> Can't place bids, ceiling too low!"
        return
    step = parameters.step()
    for order in ORDERS:
    	#print order
        if order["action"] == "BUY":
            if order["price"] >= floor:
                floor = order["price"] + step
    #print "--> Parameters for bidding: %s" % {"floor":floor, "ceiling":ceiling, "step":step}
    while floor < ceiling:
        price = floor
        qty = parameters.qty()
        symbol = parameters.symbol()

        newOrder = make_order(qty, price, 'BUY')
        newContract = make_contract(symbol)
        print "--> PLACING BID: qty %i price %0.2f" % (qty, price)
	#print "--> NO ORDER PLACED";
        con.placeOrder(id=next_order_id(), contract=newContract, order=newOrder)
        floor += step

con = None

if __name__ == '__main__':
    con = ibConnection()
    con.register(my_openorder_handler, 'OpenOrder')
    con.register(my_account_handler, 'UpdateAccountValue')
    con.register(save_order_id, 'NextValidId')
    con.register(error_handler, 'Error')
    con.register(execDetails, 'ExecDetails')
    con.register(my_tick_handler, message.TickSize, message.TickPrice)
    con.connect()
    
    while initialized == 0:
        sleep(0.1)
    print "--> Initialization complete!"


    ##con.reqAccountUpdates(1, '')
    print "-----"
    ##con.reqAllOpenOrders()
    ticker_id = gen_tick_id()
    contract = make_contract('SLV')
    con.reqMktData(ticker_id, contract, [], False)
    ##con.cancelMktData(ticker_id)
    
    ### Place sell orders
    exFilter = ExecutionFilter()
    con.reqExecutions(exFilter)

    #insertBids()

    #order = make_order(1, 25, 'BUY')
    #contract = make_contract('SLV')
    #con.placeOrder(id=next_order_id(), contract=contract, order=order)

    # Order confirmation feed
    #https://mail.google.com/mail/feed/atom/$-in-interactivebrokers/

    print "--> Looping on console..."
    while True:
        line = sys.stdin.readline()[0:-1]
        if line == "quit" or line == "exit":
            print "--> Exiting..."
            sys.exit()
        elif line == "autobuy":
            ORDERS = []
            SNOOZE = time.time() + 10
            con.reqAllOpenOrders()
            while time.time() < SNOOZE:
                sleep(0.1)
            insertBids()
        elif re.match("^buy [0-9]+@[0-9.]+$", line):
            a = line.split(" ")
            b = a[1].split("@")
            qty = int(b[0])
            price = float(b[1])
            print "Requested to purchase  %i at %f..." % (qty, price)
        
            symbol = parameters.symbol()
            newOrder = make_order(qty, price, 'BUY')
            newContract = make_contract(symbol)
            print "--> PLACING BID: qty %i price %0.2f" % (qty, price)
            con.placeOrder(id=next_order_id(), contract=newContract, order=newOrder)

