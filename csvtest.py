#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv
a=[0] * 25
b=[0] * 25
c=[0] * 25
delimit='\t'
row_number = 0
i = 0


with open('wind-4norm-load.csv', 'rb') as csvfile:
    input = csv.reader(csvfile, delimiter=delimit)
    for row in input:
        a[i], b[i], c[i] = row
        print ("a=", a[i], "b=", b[i])
        i = i + 1 
        if i == 19:
            break

with open('out.csv', 'wb') as myfile:
    wr = csv.writer(myfile)
    rows = zip(a,b)
    title = ['aaa', 'bbb']
    wr.writerow(title)
    for row in rows:
        wr.writerow(row)
        