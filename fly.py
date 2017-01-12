# -*- coding: utf-8 -*-

import time
import sys
import random
x = 0
a = 0
b = 0
c = 0
print('cube launched!')
for x in range(1000) :
   cube_score = random.randint(1,3)
   if cube_score == 1 :
      a = a + 1
   if cube_score == 2 :
      b = b + 1
   if cube_score == 3 :
      c = c + 1
   sys.stdout.write('\r'+ 'одна сторона = ' + str(a) + '; double score = ' + str(b) + '; triple score = ' + str(c))
   sys.stdout.flush()
   time.sleep(0.002)

sys.stdout.write('\n')

