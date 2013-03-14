import pandas 
from qstkutil import DataAccess as da
import numpy as np
import math
import copy
import qstkutil.qsdateutil as du
import datetime as dt
import qstkutil.DataAccess as da
import qstkutil.tsutil as tsu
import qstkstudy.EventProfiler as ep
import csv
from operator import itemgetter


print __name__ + " reading data"

percentDrop = .05
percentDropHigh = .10
daysToHold = 2
position = 1000

#Reading the Data for the list of Symbols.
startday=dt.datetime(2012,1,1)  
endday=dt.datetime(2012,12,31)
timeofday=dt.timedelta(hours=16)
timestamps = du.getNYSEdays(startday,endday,timeofday)
dataobj = da.DataAccess('Yahoo')

symbols = dataobj.get_symbols_from_list("sp5002012")
symbols.append('SPY')


# Reading the Data
close = dataobj.get_data(timestamps, symbols, "actual_close")
# Completing the Data - Removing the NaN values from the Matrix
close = (close.fillna(method='ffill')).fillna(method='backfill')

#Year,Month,Day,Symbol,Direction,Position
cols = 6
#orders = [[0] * cols for i in range(10)]
orders = []

# Calculating Daily Returns for the Market
#tsu.returnize0(close.values)
#SPYValues=close[marketSymbol]

print __name__ + " generating orders"


for symbol in symbols:
	for i in range(1,len(close[symbol])-daysToHold):

		#-----This is the event-----

		#Event if today's drop is greater than percentDrop over marketDrop and yesterday dropped > 0
		marketDrop = (close['SPY'][i-1]-close['SPY'][i])/close['SPY'][i-1]
		stockDrop = (close[symbol][i-1]-close[symbol][i])/close[symbol][i-1]
		#marketDrop1 = (close['SPY'][i-2]-close['SPY'][i-1])/close['SPY'][i-2]
		stockDrop1 = (close[symbol][i-2]-close[symbol][i-1])/close[symbol][i-2]

		if stockDrop >= percentDrop + marketDrop and stockDrop1 > 0:
			
		#-----This is the event-----

			#Add Buy and Sell order
			tempPosition = int(position/close[symbol][i])
			orders.append([timestamps[i].year,timestamps[i].month, timestamps[i].day,symbol,'Buy',tempPosition])
			orders.append([timestamps[i+daysToHold].year,timestamps[i+daysToHold].month, timestamps[i+daysToHold].day,symbol,'Sell',tempPosition])

print __name__ + " writing orders"

#Sort by day, month, then year
orders = sorted(orders, key=itemgetter(2))
orders = sorted(orders, key=itemgetter(1))
orders = sorted(orders, key=itemgetter(0))

print __name__ + " printed " + str(len(orders)/2) + " orders with total commission = $" + str(len(orders)/2*8)


myfile = open('orders.csv', 'wb')
wr = csv.writer(myfile)
wr.writerows(orders)






