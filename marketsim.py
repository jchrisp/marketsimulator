import csv
import qstkutil.qsdateutil as du
import qstkutil.tsutil as tsu
import qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
from pylab import *
import datetime as dt
import numpy

cashStart = 50000

dates = []
datesOrdered = []
symbols = []
quantity = []

print __name__ + " reading orders"

with open('orders.csv', 'rbU') as f:
    trades = csv.reader(f)
    for row in trades:
        trades_when = dt.datetime(int(row[0]), int(row[1]), int(row[2]),16)
        trade_symbol = row[3]
        trade_quantity = float(row[5])
        if row[4].lower() == 'sell':
            trade_quantity = -trade_quantity
        symbols.append(trade_symbol)
        dates.append(trades_when)
        datesOrdered.append(trades_when)
        quantity.append(trade_quantity)


datesOrdered.sort()

#Get unique symbols by switching from list to set and back
symbolsUnique = []
symbolsUnique = list(set(symbols))


startday = datesOrdered[0]
endday = datesOrdered[-1]
timeofday=dt.timedelta(hours=16)
timestamps = du.getNYSEdays(startday, endday, timeofday)

#Get Data for our specific date range
dataobj = da.DataAccess('Yahoo')
close = dataobj.get_data(timestamps,symbolsUnique,"actual_close")
close = (close.fillna(method='ffill')).fillna(method='backfill')

#Set up master list

#number of columns will be symbols we trade +2 for Date and Cash
cols = len(symbolsUnique)+2

#Hardcode the size of the 2D list
masterList = [[0] * cols for i in range(len(timestamps)+2)]

masterList[0][0] = "Dates"

for symbol in range(len(symbolsUnique)):
    masterList[0][symbol+1] = symbolsUnique[symbol]

masterList[0][cols-1] = "Cash"


#declare function to search list for multiple indices of same object
find = lambda searchList, elem: [[i for i, x in enumerate(searchList) if x == e] for e in elem]

print __name__ + " executing orders"
#populate masterList
masterList[1][cols-1] = cashStart

for row in range(len(timestamps)):
    mrow = row+2
    #Fill in date column
    masterList[mrow][0] = timestamps[row]
    #Fill in symbol columns
    for col in range(len(symbolsUnique)):
        masterList[mrow][col+1] =  masterList[mrow-1][col+1]
    #Fill in cash
    masterList[mrow][cols-1] = masterList[mrow-1][cols-1]
    tradeIndexes = [];
    #set up iteritable list for parameter in "find"
    currentDay = []
    currentDay.append(masterList[mrow][0])
    #serach if there are multiple trades in one day
    tradeDays = find(dates,currentDay)
    tradeIndexes = tradeDays[0] 
    for trade in range(len(tradeIndexes)):
        index = tradeIndexes[trade]
        #Update position in symbol
        for col in range(len(symbolsUnique)):
            if masterList[0][col+1] == symbols[index]:
                masterList[mrow][col+1] = masterList[mrow][col+1] + quantity[index]
        #Update cash
        symbolIndex = symbolsUnique.index(symbols[index])
        masterList[mrow][cols-1] = masterList[mrow][cols-1] + (float(close.ix[row,symbolIndex]))*quantity[index]*-1

#print masterList
#Make 2D list for portfolio
portfolio = [[0] * 4 for i in range(len(timestamps))]

print __name__ + " calculating values"
#Populate portfolio value per day over time range for analyze.py
for row in range(len(portfolio)):
    #Set date in first 3 columns
    tempDate = masterList[row+2][0]
    #print tempDate
    portfolio[row][0] = tempDate.year
    portfolio[row][1] = tempDate.month
    portfolio[row][2] = tempDate.day
    #Calculate portfolio value per day
    dayValue = 0
    for col in range(len(symbolsUnique)+1):
        #For each symbol add current value
        if (col != len(symbolsUnique)):
            position = float(close.ix[row,col])*masterList[row+1][col+1]
            dayValue = dayValue + position
        #Add cash
        else:
            dayValue = dayValue + masterList[row+1][len(symbolsUnique)+1]
    #Set day's value in second column
    portfolio[row][3] = dayValue

print __name__ + " writing values"

myfile = open('values.csv', 'wb')
wr = csv.writer(myfile)
wr.writerows(portfolio)

#Still need to output portfolio to csv file and accept system arguements

