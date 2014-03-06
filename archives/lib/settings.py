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

import yaml

class TradeParameters:
    bid = 0
    ask = 0
    def getParameter(self, key):
        f = open('parameters.yaml', 'r')
        temp = yaml.safe_load(f)
        f.close()
        return temp["key"]
    def spread(self):
        return self.getParameter("spread")
    def floor(self):
        return float(self.getParameter("floor"))
    def step(self):
        return float(self.getParameter("step"))
    def symbol(self):
        return "SLV"
    def tickers(self):
        return {1: "SLV"}
    def qty(self):
        return int(self.getParameter("qty"))
    def ceiling(self):
        if self.bid <= 0:
            return 0
        else:
            ceiling = self.bid

            # Gap lower so market has to drop before we buy anything
            gap = self.spread() * 0.90
            ceiling = ceiling - gap

            return ceiling

