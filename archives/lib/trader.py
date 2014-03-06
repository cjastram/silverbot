
import sys
from ib.ext.Contract import Contract
from ib.ext.EWrapper import EWrapper
from ib.ext.EClientSocket import EClientSocket
from ib.ext.ExecutionFilter import ExecutionFilter


def showmessage(message, mapping):
    try:
        del(mapping['self'])
    except (KeyError, ):
        pass
    items = mapping.items()
    items.sort()
    print '### %s' % (message, )
    for k, v in items:
        print '    %s:%s' % (k, v)

#def gen_tick_id():
    #i = randint(100, 10000)
    #while True:
        #yield i
        #i += 1
#gen_tick_id = gen_tick_id().next

class Wrapper(EWrapper):
    orders = None
    order_ids = [0]
    parameters = None
    connection = None

    def __init__(self, parameters):
        # Variable initialization
        #self.orders = orders.OrderBook()
        #self.price_log = data.PriceLog()
        #self.parameters = parameters
        
        self.connection = EClientSocket(self)
        self.connection.eConnect('localhost', 7496, 0) # host, port, clientId
        
        tick_id = 1
        symbol = "SLV"
        contract = self.makeContract(symbol)
        self.connection.reqMktData(tick_id, contract, [], False)

    def makeContract(self, symbol):
        contract = Contract()
        contract.m_symbol = symbol
        contract.m_secType = 'STK'
        contract.m_exchange = 'SMART'
        contract.m_primaryExch = 'SMART'
        contract.m_currency = 'USD'
        contract.m_localSymbol = symbol
        return contract

    def tickPrice(self, tickerId, field, price, canAutoExecute):
        #showmessage('tickPrice', vars())
        
        # 1 = bid
        # 2 = ask
        # 4 = last
        # 6 = high
        # 7 = low
        # 9 = close

        priceLog = {}

        side = ""
        if field == 2:
            print "a%0.2f " % price
        elif field == 1:
            print "b%0.2f " % price
        if side != "":
            print side, price

    def openOrder(self, orderId, contract, order, state):
        orderId = order.m_orderId
        symbol = contract.m_symbol
        qty = order.m_totalQuantity
        price = order.m_lmtPrice
        action = order.m_action
        self.orders.add(orderId, symbol, qty, price, action)
        
        order = [orderId, symbol, qty, price, action]
        print "--> Open order:%s Status:%s Warning:%s" % (order, state.m_status, state.m_warningText)
    
    def error(self, id=None, errorCode=None, errorMsg=None):
        if errorCode == 2104:
            print "--> %s" % errorMsg
        else:
            showmessage('error', vars())
    
    def nextValidId(self, orderId):
        self.order_ids.append(orderId)

    def connectionClosed(self):
        print "--> Connection closed, exiting..."
        sys.exit(0)

    def tickSize(self, tickerId, field, size): pass #showmessage('tickSize', vars())
    def tickGeneric(self, tickerId, tickType, value): pass #showmessage('tickGeneric', vars()) 
    def tickString(self, tickerId, tickType, value): pass #showmessage('tickString', vars()) 
    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints, impliedFuture, holdDays, futureExpiry, dividendImpact, dividendsToExpiry): showmessage('tickEFP', vars()) 
    def tickOptionComputation(self, tickerId, field, impliedVolatility, delta): showmessage('tickOptionComputation', vars()) 
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeId): pass #showmessage('orderStatus', vars()) 
    def openOrderEnd(self): showmessage('openOrderEnd', vars())
    def updateAccountValue(self, key, value, currency, accountName): showmessage('updateAccountValue', vars()) 
    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName): showmessage('updatePortfolio', vars()) 
    def updateAccountTime(self, timeStamp): showmessage('updateAccountTime', vars()) 
    def accountDownloadEnd(self, accountName): showmessage('accountDownloadEnd', vars()) 
    def contractDetails(self, contractDetails): showmessage('contractDetails', vars()) 
    def bondContractDetails(self, contractDetails): showmessage('bondContractDetails', vars()) 
    def contractDetailsEnd(self, reqId): showmessage('contractDetailsEnd', vars()) 
    def execDetails(self, orderId, contract, execution): showmessage('execDetails', vars()) 
    def execDetailsEnd(self, reqId): showmessage('execDetailsEnd', vars()) 
    def error_0(self, strval): showmessage('error_0', vars()) 
    def error_1(self, strval): showmessage('error_1', vars()) 
    def updateMktDepth(self, tickerId, position, operation, side, price, size): showmessage('updateMktDepth', vars()) 
    def updateMktDepthL2(self, tickerId, position, marketMaker, operation, side, price, size): showmessage('updateMktDepthL2', vars()) 
    def updateNewsBulletin(self, msgId, msgType, message, origExchange): showmessage('updateNewsBulletin', vars()) 
    def managedAccounts(self, accountsList): pass #showmessage('managedAccounts', vars()) 
    def receiveFA(self, faDataType, xml): showmessage('receiveFA', vars()) 
    def historicalData(self, reqId, date, open, high, low, close, volume, count, WAP, hasGaps): showmessage('historicalData', vars()) 
    def scannerParameters(self, xml): showmessage('scannerParameters', vars()) 
    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection): showmessage('scannerData', vars()) 
    def scannerDataEnd(self, reqId): showmessage('scannerDataEnd', vars()) 
    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count): showmessage('realtimeBar', vars()) 
    def currentTime(self, time): showmessage('currentTime', vars()) 
    def fundamentalData(self, reqId, data): showmessage('fundamentalData', vars()) 
    def deltaNeutralValidation(self, reqId, underComp): showmessage('deltaNeutralValidation', vars()) 
    def tickSnapshotEnd(self, reqId): showmessage('tickSnapshotEnd', vars()) 
    def marketDataType(self, reqId, marketDataType): showmessage('marketDataType', vars()) 
    def commissionReport(self, commissionReport): showmessage('commissionReport', vars()) 


#class App:
    #parameters = None
    #def __init__(self, host='localhost', port=7496, clientId=0):
        #self.host = host
        #self.port = port
        #self.clientId = clientId
        ##self.parameters = settings.TradeParameters()
        #self.wrapper = Wrapper(self.parameters)
        #self.connection = EClientSocket(self.wrapper)
        #
    #def eConnect(self):
        #self.connection.eConnect(self.host, self.port, self.clientId)
#
    #def reqAccountUpdates(self):
        #self.connection.reqAccountUpdates(1, '')
#
    #def reqOpenOrders(self):
        #self.connection.reqOpenOrders()
#
    #def reqExecutions(self):
        #filt = ExecutionFilter()
        #self.connection.reqExecutions(filt)
    ##def reqIds(self):
        ##self.connection.reqIds(10)
    ##def reqNewsBulletins(self):
        ##self.connection.reqNewsBulletins(1)
    ##def cancelNewsBulletins(self):
        ##self.connection.cancelNewsBulletins()
    ##def setServerLogLevel(self):
        ##self.connection.setServerLogLevel(3)
    ##def reqAutoOpenOrders(self):
        ##self.connection.reqAutoOpenOrders(1)
    ##def reqAllOpenOrders(self):
        ##self.connection.reqAllOpenOrders()
    ##def reqManagedAccts(self):
        ##self.connection.reqManagedAccts()
    ##def requestFA(self):
        ##self.connection.requestFA(1)
    ##def reqMktData(self):
        ##tick_id = 1
        ##symbol = "SLV"
        ##contract = self.wrapper.makeContract(symbol)
        ##self.connection.reqMktData(tick_id, contract, [], False)
    ##def reqHistoricalData(self):
        ##contract = Contract()
        ##contract.m_symbol = 'QQQQ'
        ##contract.m_secType = 'STK'
        ##contract.m_exchange = 'SMART'
        ##endtime = strftime('%Y%m%d %H:%M:%S')
        ##self.connection.reqHistoricalData(
            ##tickerId=1,
            ##contract=contract,
            ##endDateTime=endtime,
            ##durationStr='1 D',
            ##barSizeSetting='1 min',
            ##whatToShow='TRADES',
            ##useRTH=0,
            ##formatDate=1)
#
    #def eDisconnect(self):
        #sleep(5)
        #self.connection.eDisconnect()
