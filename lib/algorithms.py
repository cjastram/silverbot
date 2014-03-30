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
        self.place_offsets()

    def place_offsets(self):
        print("--> Placing offsets.")
        offset = 0.50
        self.storage.get_lock("place-offsets")
        #sheet = self._spreadsheet.worksheet("Book")
        for order in self.storage.query_orders({"status": "filled", "side": "bid"}):
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
        self.storage.release_lock("place-offsets")


#    def _confirm_hypothetical(self, side, price, qty):
#        print "--> Confirming hypothetical %s order for %i at %0.02f." % (side, qty, price)
#        sheet = self._spreadsheet.worksheet("Book")
#        data = { 
#            "id": "%ID%", "side": side, "price": price, "qty": qty,
#            "status": "imagined", "imagined": self._timestamp()
#        }
#        recorded = False
#        for row in self._select(sheet, "status", "imagined"):
#            if self._equivalent(row["price"], data["price"]):
#                recorded = True
#
#                ### Check and reset quantity if necessary
#                if int(row["qty"]) != int(data["qty"]):
#                    print "--> Updating quantity for order %s from %s to %s." % (row["id"], row["qty"], data["qty"])
#                    sheet.update_cell(row["id"], self.schema[sheet.title]["qty"], data["qty"])
#                    
#                break
#        if not recorded:
#            self._add(sheet, data)
#        
#    def set_hypothetical_bids(self, bids):
#        self.get_lock("set-hypothetical-bids")
#        sheet = self._spreadsheet.worksheet("Book")
#        for bid in bids:
#            bid_id = self._confirm_hypothetical("bid", bid[0], bid[1])
#
#        for row in self._select(sheet, "status", "imagined"):
#            desired = False
#            for bid in bids:
#                if self._equivalent(bid[0], row["price"]):
#                    desired = True
#                    break
#            if not desired:
#                sheet.update_cell(row["id"], self.schema[sheet.title]["status"], "Forgotten")
#        self.release_lock("set-hypothetical-bids")


