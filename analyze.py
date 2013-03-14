import csv
import qstkutil.qsdateutil as du
import qstkutil.tsutil as tsu
import qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
from pylab import *
import datetime as dt
import numpy

dates = []
values = []
benchmarks = []
benchmark = "$SPX"
benchmarks.append(benchmark)

with open('values.csv', 'rbU') as f:
    trades = csv.reader(f)
    for row in trades:
        day = dt.datetime(int(row[0]), int(row[1]), int(row[2]),16)
        dailyValue = row[3]
        dates.append(day)
        values.append(dailyValue)

dataobj = da.DataAccess('Yahoo')
benchmarkClose = dataobj.get_data(dates,benchmarks,"actual_close")
benchmarkClose = (benchmarkClose.fillna(method='ffill')).fillna(method='backfill')

#Set initial position for benchmark
benchmarkPosition = float(values[0])/float(benchmarkClose.ix[0,0])

#Set up 2d list
allValues = [[0] * 2 for i in range(len(dates))]

#Populate fund value and benchmarks into allValues
for row in range(len(dates)):
    allValues[row][0] = values[row]
    allValues[row][1] = float(benchmarkClose.ix[row,0])*benchmarkPosition

#plot fund vs benchmarks
plt.clf()
plt.plot(dates,allValues)
#plt.legend(["Fund",benchmark])
plt.ylabel('Value')
plt.xlabel('Date')
savefig('fund.pdf',format='pdf')

#Calculate metrics

#return
fundReturn = (float(allValues[len(dates)-1][0]) - float(allValues[0][0])) / float(allValues[0][0])*100
benchmarkReturn = (float(allValues[len(dates)-1][1]) - float(allValues[0][1])) / float(allValues[0][1])*100


print "-------Metrics---------"
print "Fund return: " + str(fundReturn)+"%"
print "Benchmark return: " + str(benchmarkReturn)+"%"



