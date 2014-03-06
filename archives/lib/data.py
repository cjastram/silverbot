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
import time
import yaml

class OffsetExecutions:
    def load(self):
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
    def save(self, executions):
        f = file('offsetExecutions.yaml', 'w')
        yaml.dump(executions, f, default_flow_style=False)

class PriceLog:
    def save(self, side, price):
        priceLog = {}
        date = datetime.date.today()
        priceLogFile = "/tmp/%s.yaml" % date.strftime("%Y-%m-%d")
        try:
            f = open(priceLogFile, 'r')
            temp = yaml.safe_load(f)
            f.close()
            priceLog = temp
        except Exception as e:
            pass
                
        priceLog[time.time()] = [side, price]
        f = open(priceLogFile, "w" )
        yaml.dump(priceLog, f) #, default_flow_style=False)
        f.close()
        if len(priceLog) % 10 == 0:
            print " "

