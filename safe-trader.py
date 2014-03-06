#!/usr/bin/env python
#
#
#

from lib import trader, data
import gspread
import sys
import time

class Algorithm:
   storage = None
   def __init__(self, storage):
      market_price = 20.71
      quantity = 20
      spread = 0.50
      interval = 0.50
      pool = 2000.00
      base = 18.00

      self.storage = storage

      price = base
      purchase_points = []
      while price < market_price:
         purchase_points.append(price)
         price += interval

      bids = []
      while len(purchase_points):
         order_price = purchase_points.pop()
         order_quantity = quantity
         order_amount = price * quantity
         if order_amount > pool:
            break

         bids.append([order_price, order_quantity])
         pool = pool - order_amount

      #self.storage.set_hypothetical_bids(bids)
      self.storage.place_offsets()


if __name__ == '__main__':
   s = data.Storage()

   app = trader.Wrapper(None)
   #app = trader.App()

   #app.eConnect()
   #app.reqMktData()
   
   while True:
      line = sys.stdin.readline()[0:-1]
      if line == "quit" or line == "exit":
         print "--> Exiting..."
         sys.exit()


#a = Algorithm(s)
