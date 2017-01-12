#! /usr/bin/env python
# -*- coding: utf-8 -*-
 
from functions import read_csv, draw_chart # импорт функции read_csv из файла function_read_csv
 
matritsa_dobychi = []
zeroes = []
well_profile = []
dobycha = []
new_wells = read_csv('dpr_new_oil.csv', 1) # присваивание переменной содержимого первого столбца( количество нововведенных скважин за каждый месяц) файла test.csv с помощью функции read_csv
for i in range(200):
 new_wells.append(226890.599245)
for i in range(144):
   
   well_profile.append( 1 / ((1 + 0.15 * i) ** 0.98)) # добавление к массиву well_profile значения добычи скважины за каждый(i) месяц 
   
   # по окончанию цикла создается массив со значениями добычи одной скважины за каждый(i) месяц
   
for i in range(321):
   
   row_matrix = []
   
   if i >= 1:
      zeroes.append(0) # каждую итерацию цикла для значения i, большего или равного 1(в данном случае имеются ввиду элементы массива new_wells), в будущий массив с нулями добавляется элемент '0'
      
   row_matrix.extend(zeroes) # каждую итерацию цикла в массив добавляется массив с нулями
   
   for j in range(144):

      row_matrix.append(float(new_wells[i]) * well_profile[j]) # каждую итерацию цикла в массив, где уже есть массив с нулями, добавляются элементы массива new_wells(количество нововведенных скважин за каждый месяц), преобразованные в числа и перемноженные на элементы массива well_profile(значения добычи скважины за каждый(i) месяц)
      
   matritsa_dobychi.append(row_matrix) # каждую итерацию цикла в матрицу добавляется новая строка, содержащая массив с нулями и массив с ежемесячной добычей нововведенных скважин
   
matrix_transposed = map(list, zip(*matritsa_dobychi)) #создание транспонированной матрицы из оригинальной для удобства нахождения добычи
for i in range(144) :
    dobycha.append(sum(matrix_transposed[i])) # создание массива с добычей
    
print(dobycha)