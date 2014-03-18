#
#   SilverBot is a Python application to interact with IB's TWS API.
#   Copyright (C) 2013 Christopher Jastram <cjastram@gmail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#import datetime
#import gspread
#import time
#import yaml

class SimpleOffset:
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

   def place_offsets(self):
      print "--> Placing offsets."
      offset = 0.50
      self.storage._setConfig("Working", "Offsets")
      #sheet = self._spreadsheet.worksheet("Book")
      for order in self.storage.query({"status": "filled"}):
         side = "ask"
         price = order.price + offset
         qty = order.qty

         order.status = "offset"
         order.offset = self.storage._timestamp()

         #data = { 
            #"id": "%ID%", "side": side, "price": price, "qty": qty,
            #"status": "imagined", "imagined": self._timestamp(), "parent": row["id"],
         #}
         #sheet.update_cell(row["id"], self.schema[sheet.title]["status"], "offset")
         #sheet.update_cell(row["id"], self.schema[sheet.title]["offset"], self._timestamp())
         #self._add(sheet, data)

