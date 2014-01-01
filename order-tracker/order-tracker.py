#!/usr/bin/env python
#
# This file is part of Silverbot.
#
# Silverbot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Silverbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Silverbot.  If not, see <http://www.gnu.org/licenses/>.
#

from urllib2 import urlopen
from xml.sax import make_parser, ContentHandler, parseString
import base64
import os
import re
import sys
import urllib2
import yaml

class GMailHandler (ContentHandler):

    def __init__(self):
        ContentHandler.__init__(self)
        self.__inItem = False
        self.__inTitle = False
        self.__inIssued = False
        self.title = ""
        self.issued = ""
        self.entries = []
  
    def characters(self,data):
        if self.__inTitle:
            self.title = self.title + data.encode('ascii', 'ignore')
        if self.__inIssued:
            self.issued = self.issued + data.encode('ascii', 'ignore')
         
    def startElement(self, tag, attrs):
        if tag == "entry":
            self.__inItem = True
        if tag == "issued" and self.__inItem:
            self.__inIssued = True
        if tag == "title" and self.__inItem:
            self.__inTitle = True
  
    def endElement(self, tag):
        if tag == "title" and self.__inTitle:
            self.__inTitle = False
        if tag == "issued" and self.__inIssued:
            self.__inIssued = False
        if tag == "entry":
            self.__inItem = False
            m = re.match(r"(BOUGHT|SOLD) ([0-9]+) ([^ (]+).* @ ([0-9]+)", self.title)
            if m:
                entry = {"action": m.group(1), "qty": float(m.group(2)), "symbol": m.group(3), "price": float(m.group(4))}
                entry["filled"] = self.issued
                entry["order_number"] = "unknown"
                self.entries.append(entry)
            self.title = ""
            self.issued = ""

url = os.environ['gmail_url']
username = os.environ['gmail_login']
password = os.environ['gmail_password']
req = urllib2.Request(url)
authstr = base64.encodestring("%s:%s" % (username, password))[:-1]
req.add_header("Authorization", "Basic " + authstr)
infile = urllib2.urlopen(req)

handler = GMailHandler()
parser = make_parser()
parser.setContentHandler(handler)
parser.parse(infile)

stream = file('orders.yaml', 'w')
yaml.dump(handler.entries, stream, default_flow_style=False)

