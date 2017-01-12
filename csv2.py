#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv



def test(columns_to_return):
    data=[1,2,3,4,5]
    return tuple(data[:columns_to_return])


a1,a2,a3,a4=test(4)
print(a4)

a = []
b = []

with open('out.csv','r') as f:
    parameters = csv.reader(f, delimiter = ';')
    for row in parameters :
        a = row
        b = row
     #   c = list(parameters)
     #   b = list(parameters)
     

with open('out.csv') as f:
    for row in f :
        a = row
print ('a=', a)
print ('b=', b)