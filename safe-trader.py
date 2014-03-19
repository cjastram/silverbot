#!/usr/bin/env python
#
#
#

from lib import trader, data, algorithms
import gspread
import sys
import time


if __name__ == '__main__':
   s = data.Storage()
   print s.get_lock("offsets")
   print s.release_lock("offsets")
   print s.get_lock("offsets")
   #a = algorithms.SimpleOffset(s)

   ##app = trader.Wrapper(None)
   #
   ##while True:
      ##line = sys.stdin.readline()[0:-1]
      ##if line == "quit" or line == "exit":
         ##print "--> Exiting..."
         ##sys.exit()


