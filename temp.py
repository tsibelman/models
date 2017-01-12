import pandas
per = 12
s = pandas.date_range('2012-1-1', periods=per, freq='MS')
print s[2]

#a = [d.strftime('%d.%m.%y') for d in pandas.date_range('20130101','20150201', freq = 'MS')]
#b = 10

#print a
