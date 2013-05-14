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
import urllib
import yaml

ORDERS = []
EXECUTIONS = {}

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
        return 12
    def ceiling(self):
        data = []
        url = 'http://finance.yahoo.com/d/quotes.csv?s='
        for s in 'slv'.split():
            url += s+"+"
        url = url[0:-1]
        url += "&f=sb3b2l1l"
        f = urllib.urlopen(url,proxies = {})
        rows = f.readlines()
        for r in rows:
            values = [x for x in r.split(',')]
            symbol = values[0][1:-1]
            bid = float(values[1])
            ask = float(values[2])
            last = float(values[3])
            data.append({"symbol":symbol,"bid":bid,"ask":ask,"last":last,"time":values[4]})
        #return data[0] # might change this for multi-symbol support, eventually

        # Market sell price is literal ceiling
        ceiling = data[0]["ask"]

        # Gap lower so market has to drop before we buy anything
        gap = self.spread() * 0.90
        ceiling = ceiling - gap

        return ceiling

dataHandler = DataHandler()
parameters = Parameters()

def my_account_handler(msg):
    print msg

def my_tick_handler(msg):
    print msg

def my_openorder_handler(msg):
    global ORDERS
    orderId = msg.orderId
    orderState = msg.orderState
    order = {}
    order["orderId"] = msg.order.m_orderId
    order["symbol"] = msg.contract.m_symbol
    order["qty"] = msg.order.m_totalQuantity
    order["price"] = msg.order.m_lmtPrice
    order["action"] = msg.order.m_action
    ORDERS.append(order)

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
    orderId = msg.orderId

    if order["side"] == "BOT":
        executions = dataHandler.loadOffsetExecutions()
        if not orderId in executions:
            executions[orderId] = order

            spread = parameters.spread()
            qty = order["qty"]
            symbol = parameters.symbol()
            price = order["price"] + spread
            newOrder = make_order(qty, price, 'SELL')
            newContract = make_contract(symbol)
            print "--> execDetails: %i shares bought at %f (#%s), selling at %f" % (qty, order["price"], orderId, price)
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
    print "-->Initialization complete!"

    ### Place sell orders
    exFilter = ExecutionFilter()
    con.reqExecutions(exFilter)

    ### Place buy orders
    floor = parameters.floor()
    ceiling = parameters.ceiling()
    step = parameters.step()
    for order in ORDERS:
        if order["action"] == "BUY":
            if order["price"] > floor:
                floor = order["price"] + step
    while floor < ceiling:
        price = floor
        qty = parameters.qty()
        symbol = parameters.symbol()

        newOrder = make_order(qty, price, 'BUY')
        newContract = make_contract(symbol)
        print "--> main: placing bid for %i shares at %f" % (qty, price)
        con.placeOrder(id=next_order_id(), contract=newContract, order=newOrder)
        floor += step


    ##con.reqAccountUpdates(1, '')
    ##print "-----"
    ##con.reqAllOpenOrders()
    ##ticker_id = gen_tick_id()
    ##con.reqMktData(ticker_id, contract, [], True)
    ##con.cancelMktData(ticker_id)

    #order = make_order(1, 25, 'BUY')
    #contract = make_contract('SLV')
    #con.placeOrder(id=next_order_id(), contract=contract, order=order)

    # Order confirmation feed
    #https://mail.google.com/mail/feed/atom/$-in-interactivebrokers/

    sleep(5)
