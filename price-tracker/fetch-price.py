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

#def get_quote(symbol):
#symbol = 'SLV'
#base_url = 'http://finance.google.com/finance?q='
#content = urllib.urlopen(base_url + symbol).read()
#m = re.search('id="ref_694653_l".*?>(.*?)<', content)
#if m:
  #quote = m.group(1)
#else:
  #quote = 'no quote available for: ' + symbol
#print quote

import datetime
import re
import string
import sys
import urllib
import yaml

symbols = 'slv'.split()

def get_data():
    data = []
    url = 'http://finance.yahoo.com/d/quotes.csv?s='
    for s in symbols:
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
    return data[0] # might change this for multi-symbol support, eventually

quote = get_data()
if quote["bid"] < 1:
    print "Error: Inaccurate quote returned, exiting..."
    sys.exit(1)

dataset = {}
filename = datetime.datetime.now().strftime("%Y-%m-%d")
filename = "output/" + filename + ".yaml"
try:
    f = open(filename, "r")
    dataset = yaml.load(f)
except IOError:
    dataset = {}
    
dateStamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
dataset[dateStamp] = quote

print quote

# Any error here, we want to be fatal
f = open(filename, "w")
yaml.dump(dataset, f, width=200)
f.close()

