#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv

# CSV

csv_input_file = 'wind-4norm-load.csv' # Имя файла с вводными данными. Формат столбцов: ветер в Германии, нормировка на 4 страны, загрузка в Германии. Хранить в том же каталоге.
csv_output_file = "output4.csv"
col_delimiter='\t' # делимитер для CSV файла
row_number = 0 # обнуление счётчика строк
hours_to_analyze = 100 * 24 # cколько часов (строк) анализировать

# объявление массивов входных данных

wind_germany = [0] * hours_to_analyze
wind_normalized = [0] * hours_to_analyze
load_germany = [0] * hours_to_analyze

# объявление массивов анализируемых данных

accumulated = [0] * hours_to_analyze
charged = [0] * hours_to_analyze
discharged = [0] * hours_to_analyze
gas = [0] * hours_to_analyze
overhead = [0] * hours_to_analyze
inbattery_list = [0] * hours_to_analyze

i = 0 # обнуление переменной цикла по часам
capacity = 73 * 24 # ёмкость аккумуляции в ГВт*ч
inbattery = 0 # обнуление аккумулированной электроэнергии
wind_multiply_number = 4 # во сколько раз увеличить модельную генерацию ветра

# cчитать CSV-файл в массив нужной длины

with open(csv_input_file, 'rb') as input_file:
    input = csv.reader(input_file, delimiter=col_delimiter)
    for row in input:
        wind_germany[row_number], wind_normalized[row_number], load_germany[row_number] = row
        wind_germany[row_number] = float(wind_germany[row_number])
        wind_normalized[row_number] = float(wind_normalized[row_number]) * wind_multiply_number
        load_germany[row_number] = float(load_germany[row_number])
        row_number = row_number + 1
        if row_number == hours_to_analyze :
            break

input_file.close()

# основной цикл по часам

for i in range(hours_to_analyze) :

   if load_germany[i] > wind_normalized[i] :      # если идёт разрядка
      if load_germany[i] - wind_normalized[i] < inbattery :     # если в батарее достаточно ээ, то вычисляем сколько нужно и вычитаем
         discharged[i] = load_germany[i] - wind_normalized[i]
         inbattery = inbattery - discharged[i]      # вычисляем новый уровень батареи
         inbattery_list[i] = inbattery
         
      else:       # если в батарее недостаточно ээ, то
         discharged[i] = inbattery
         inbattery = 0
         gas[i] = load_germany[i] - wind_normalized[i] - discharged[i]
         inbattery_list[i] = inbattery
         
   else:         # идёт зарядка
      if wind_normalized[i] - load_germany[i] < capacity - inbattery :     # если в аккуме хватает места
         charged[i] = wind_normalized[i] - load_germany[i]
         inbattery = inbattery + wind_normalized[i] - load_germany[i]
         inbattery_list[i] = inbattery
         
      else: # если в аккуме не хватает места
         charged[i] = capacity - inbattery
         inbattery = capacity
         overhead[i] = wind_normalized[i] - load_germany[i] - charged[i]
         inbattery_list[i] = inbattery
   
   #print("wind_normalized=", wind_normalized[i], "load_germany=", load_germany[i], "charged=", charged[i], "discharged=", discharged[i], "inbattery=", inbattery, "overhead=", overhead[i], "gas=", gas[i])
   i = i + 1

i = 0
with open(csv_output_file, 'wb') as output_file:
    #write = csv.writer(output_file, quoting=csv.QUOTE_ALL)
    write = csv.writer(output_file)
    rows = zip(wind_normalized, load_germany, charged, discharged, inbattery_list, overhead, gas)
    title = ['wind_normalized', 'load_germany', 'charged', 'discharged', 'inbattery', 'overhead', 'gas']
    write.writerow(title)
    for row in rows:
        write.writerow(row)
        if i == hours_to_analyze :
            break
        i = i + 1

output_file.close()
print ("max overhead=", max(overhead), '\n', 'max gas=', max(gas), "max wind=", max(wind_normalized), "max load=", max(load_germany))


'''
f=open('inbattery.txt','w')
#s1='\n'.join(str(charged))
#f.write(s1)
#f.close()

with open('windandload.csv', 'rb') as csvfile:
    input = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
      print ', '.join(row)
'''