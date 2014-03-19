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

import datetime
import gspread
import time
import yaml

_GDOC = None

class Order(object):
    schema = [ "id", "side", "price", "qty", "status", "imagined", "requested", "confirmed", "filled", "offset", "cancelled", "parent" ]
    def __init__(self, row):
        self._id = row["id"]
        self._side = row["side"]
        self._price = row["price"]
        self._qty = row["qty"]
        self._status = row["status"]
        self._imagined = row["imagined"]
        self._requested = row["requested"]
        self._confirmed = row["confirmed"]
        self._filled = row["filled"]
        self._offset = row["offset"]
        self._cancelled = row["cancelled"]
        self._parent = row["parent"]

    @property
    def id(self):
        return int(self._id)
    
    @property
    def side(self):
        return self._side

    @property
    def price(self):
        return float(self._price)
    
    @property
    def qty(self):
        return int(self._qty)
    
    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        self._status = value
        s = Storage()
        s.update(self)
        
    @property
    def imagined(self): return self._imagined
    @property
    def requested(self): return self._requested
    @property
    def confirmed(self): return self._confirmed
    @property
    def filled(self): return self._filled

    @property
    def offset(self): 
        return self._offset
    @offset.setter
    def offset(self, value):
        self._offset = value
        s = Storage()
        s.update(self)
        return self._offset

    @property
    def cancelled(self): return self._cancelled
    @property
    def parent(self): return self._parent

class Storage:
    schema = {} # Static variable
    _spreadsheet = None

    def __init__(self):
        global _GDOC
        if _GDOC is None:
            f = open('auth.yaml', 'r')
            auth = yaml.safe_load(f)
            f.close()

            gc = gspread.login(auth["gdoc-login"], auth["gdoc-password"])
            spreadsheet = gc.open("Silverbot 2014")

            schema = {
                #"Pairs": [
                    #"BidID", "BidDate", "BidQty", "BidPrice", "BidStatus", 
                    #"AskID", "AskDate", "AskQty", "AskPrice", "AskStatus"],
                "Config": [ "setting", "value" ],
                "Book": [ "id", "side", "price", "qty", "status", "imagined", "requested", "confirmed", "filled", "offset", "cancelled", "parent" ],
            }

            for title, headers in schema.iteritems():
                self.schema[title] = {}

                print "--> Initializing worksheet: %s" % title

                try:
                    worksheet = spreadsheet.worksheet(title)
                except gspread.exceptions.WorksheetNotFound:
                    worksheet = spreadsheet.add_worksheet(title=title, rows=1, cols=20)

                row = worksheet.row_values(1)
                for heading in headers:
                    if not heading in row:
                        col = 1
                        while col < 99:
                            val = worksheet.cell(1, col).value
                            if val == "":
                                worksheet.update_cell(1, col, heading)
                                break
                            col = col + 1
                col = 1
                for heading in worksheet.row_values(1):
                    if not heading is None:
                        if heading in self.schema[title]:
                            print "Duplicate heading %s in sheet %s, avoid this!" % (heading, title)
                        self.schema[title][heading] = col
                    col = col + 1

            #wks.update_acell('B2', "it's down there somewhere, let me take another look.")

            # Fetch a cell range
            #cell_list = wks.range('A1:B7')
            _GDOC = spreadsheet
        self._spreadsheet = _GDOC

    def get_lock(self, lock):
        """Set a lock, returns True if lock was successfully obtained but otherwise False."""
        key = "lock-%s" % lock
        value = self._get_config(key)
        if not len(value):
            self._set_config(key, self._timestamp())
            return True
        else:
            return False

    def release_lock(self, lock):
        """Release a lock once you are finished."""
        key = "lock-%s" % lock
        self._set_config(key, "")

    def _timestamp(self):
        return time.strftime("%m/%d/%Y %H:%M:%S", time.localtime())

    def _equivalent(self, a, b):
        a = float(a)
        b = float(b)
        margin = 0.001
        if a < b + margin and a > b - margin:
            return True
        else:
            return False

    def _select(self, sheet, header, value):
        result = []
        column = sheet.col_values(self.schema[sheet.title][header])
        headers = sheet.row_values(1)
        for i in range(1, len(column)):
            if column[i] == value:
                row = sheet.row_values(i+1)
                block = {}
                for i in range(0, len(headers)):
                    block[headers[i]] = None
                    if i < len(row):
                        block[headers[i]] = row[i]
                result.append(block)
        return result

    def query(self, criteria):
        sheet = self._spreadsheet.worksheet("Book")
        if len(criteria) > 1:
            raise Exception("Need to implement multi-column selection!")

        result = []
        for key, value in criteria.iteritems():
            column = sheet.col_values(self.schema[sheet.title][key])
            headers = sheet.row_values(1)
            for i in range(1, len(column)):
                if column[i] == str(value):
                    row = sheet.row_values(i+1)
                    block = {}
                    for i in range(0, len(headers)):
                        block[headers[i]] = None
                        if i < len(row):
                            block[headers[i]] = row[i]
                    order = Order(block)
                    result.append(order)
        return result

    def update(self, order):
        sheet = self._spreadsheet.worksheet("Book")

        # Retrieve old order
        old = self.query({"id": order.id})
        if len(old) != 1: 
            raise Exception("Failed to find single order by ID!")
        else:
            old = old[0]

        # Compute order delta
        update = {}
        for field in Order.schema:
            if getattr(old, field) != getattr(order, field):
                update[field] = getattr(order, field)

        # Update only changed fields
        for key, value in update.iteritems():
            sheet.update_cell(order.id, self.schema["Book"][key], value)

    def _add(self, sheet, values):
        flat = []
        count = 0
        id = sheet.row_count + 1
        while count < len(values):
            added = False
            for key, value in values.iteritems():
                if len(flat)+1 == self.schema[sheet.title][key]:
                    if value == "%ID%":
                        value = id
                    flat.append(value)
                    count = count + 1
                    added = True
            if not added:
                flat.append("")
        sheet.append_row(flat)
        return id
        
        #for key, value in values.iteritems():
        #   sheet.update_cell(row, self.schema[sheet_name][key], value)

    

    def _get_config(self, key, default=None):
        sheet = self._spreadsheet.worksheet("Config")
        index = None
        try:
            keys = sheet.col_values(1)
            index = keys.index(key) + 1
        except ValueError:
            # Config doesn't exist, add it!
            value = ""
            if not default is None:
                value = default
            sheet.append_row([key, value])
            keys = sheet.col_values(1)
            index = keys.index(key) + 1
        return sheet.cell(index, 2).value
    
    def _set_config(self, key, value):
        sheet = self._spreadsheet.worksheet("Config")
        index = None
        try:
            keys = sheet.col_values(1)
            index = keys.index(key) + 1
            sheet.update_cell(index, 2, value)
        except ValueError:
            # Config doesn't exist, add it!
            sheet.append_row([key, value])
            keys = sheet.col_values(1)
            index = keys.index(key) + 1

    def _confirm_hypothetical(self, side, price, qty):
        print "--> Confirming hypothetical %s order for %i at %0.02f." % (side, qty, price)
        sheet = self._spreadsheet.worksheet("Book")
        data = { 
            "id": "%ID%", "side": side, "price": price, "qty": qty,
            "status": "imagined", "imagined": self._timestamp()
        }
        recorded = False
        for row in self._select(sheet, "status", "imagined"):
            if self._equivalent(row["price"], data["price"]):
                recorded = True

                ### Check and reset quantity if necessary
                if int(row["qty"]) != int(data["qty"]):
                    print "--> Updating quantity for order %s from %s to %s." % (row["id"], row["qty"], data["qty"])
                    sheet.update_cell(row["id"], self.schema[sheet.title]["qty"], data["qty"])
                    
                break
        if not recorded:
            self._add(sheet, data)
        
    def set_hypothetical_bids(self, bids):
        self.get_lock("set-hypothetical-bids")
        sheet = self._spreadsheet.worksheet("Book")
        for bid in bids:
            bid_id = self._confirm_hypothetical("bid", bid[0], bid[1])

        for row in self._select(sheet, "status", "imagined"):
            desired = False
            for bid in bids:
                if self._equivalent(bid[0], row["price"]):
                    desired = True
                    break
            if not desired:
                sheet.update_cell(row["id"], self.schema[sheet.title]["status"], "Forgotten")
        self.release_lock("set-hypothetical-bids")


