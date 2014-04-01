#!/usr/bin/env python

from lib import trader, data, algorithms
import time

if __name__ == '__main__':
    s = data.Storage()
    #a = algorithms.SimpleOffset(s)

    tws = trader.Wrapper(s)
    while tws.connected():
        time.sleep(1)

        ### TODO: Try to reconnect if connection broken

