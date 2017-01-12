#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv

# входные данные, помимо входного CSV

hours_to_analyze = 190 * 24 # cколько часов (строк) анализировать
wind_multiply_number = 2.5 # во сколько раз увеличить модельную (равномерную по 4-м странам) генерацию ветра
solar_multiply_number = 4.7 # во сколько раз увеличить реальную генерацию солнца
capacity = 54 * 24 # ёмкость аккумуляции в ГВт*ч. 54*24 ГВт*ч эквивалентно суточному потреблению.

# CSV

csv_input_file = 'wind-4norm-solar-load.csv' # Имя файла с вводными данными. Формат столбцов: ветер в Германии, нормировка на 4 страны, загрузка в Германии. Хранить в том же каталоге.
csv_output_file = "output7.csv"
col_delimiter='\t' # делимитер для CSV файла

# объявление массивов входных данных

wind_germany = [0] * hours_to_analyze
wind_normalized = [0] * hours_to_analyze
load_germany = [0] * hours_to_analyze
solar_germany = [0] * hours_to_analyze

# объявление массивов анализируемых данных

accumulated = [0] * hours_to_analyze
charged = [0] * hours_to_analyze
discharged = [0] * hours_to_analyze
gas = [0] * hours_to_analyze
overhead = [0] * hours_to_analyze
inbattery_list = [0] * hours_to_analyze

i = 0 # обнуление переменной цикла по часам
inbattery = 0 # обнуление аккумулированной электроэнергии
overhead_count = 0 # обнуление счётчика превышений генерации над потреблением и аккумуляцией

# cчитать CSV-файл в массив нужной длины

with open(csv_input_file, 'rb') as input_file:
    input = csv.reader(input_file, delimiter = col_delimiter)
    for row in input:
        wind_germany[i], wind_normalized[i], solar_germany[i], load_germany[i] = row
        wind_germany[i] = float(wind_germany[i])
        wind_normalized[i] = float(wind_normalized[i]) * wind_multiply_number
        solar_germany[i] = float(solar_germany[i]) * solar_multiply_number
        load_germany[i] = float(load_germany[i])
        i = i + 1
        if i == hours_to_analyze :
            break

input_file.close()

# основной цикл по часам

for i in range(hours_to_analyze) :

   if load_germany[i] > wind_normalized[i] + solar_germany[i]:      # если идёт разрядка
      if load_germany[i] - wind_normalized[i] - solar_germany[i] < inbattery :     # если в батарее достаточно ээ, то вычисляем сколько нужно и вычитаем
         discharged[i] = load_germany[i] - (wind_normalized[i] + solar_germany[i])
         inbattery = inbattery - discharged[i]      # вычисляем новый уровень батареи
         inbattery_list[i] = inbattery
         
      else:       # если в батарее недостаточно ээ, то
         discharged[i] = inbattery
         inbattery = 0
         gas[i] = load_germany[i] - (wind_normalized[i] + solar_germany[i]) - discharged[i]
         inbattery_list[i] = inbattery
         
   else:         # идёт зарядка
      if wind_normalized[i] + solar_germany[i] - load_germany[i] < capacity - inbattery :     # если в аккуме хватает места
         charged[i] = wind_normalized[i] + solar_germany[i] - load_germany[i]
         inbattery = inbattery + wind_normalized[i] + solar_germany[i] - load_germany[i]
         inbattery_list[i] = inbattery
         
      else: # если в аккуме не хватает места
         charged[i] = capacity - inbattery
         inbattery = capacity
         overhead[i] = wind_normalized[i] + solar_germany[i] - load_germany[i] - charged[i]
         inbattery_list[i] = inbattery
         overhead_count = overhead_count + 1
   
   i = i + 1

i = 0
with open(csv_output_file, 'wb') as output_file:
    write = csv.writer(output_file)
    rows = zip(wind_normalized, solar_germany, load_germany, charged, discharged, inbattery_list, overhead, gas)
    title = ['wind_normalized', 'solar_germany', 'load_germany', 'charged', 'discharged', 'inbattery', 'overhead', 'gas']
    write.writerow(title)
    for row in rows:
        write.writerow(row)
        if i == hours_to_analyze :
            break
        i = i + 1

output_file.close()

print ('\n' + 'overhead count = ' + str(overhead_count) + ' Hours')
print ('max overhead = ' + str(format(max(overhead), '.2f') + ' GW'))
print ('max gas = ' + str(format(max(gas), '.2f') + ' GW'))
print ('max wind = ' + str(format(max(wind_normalized), '.2f') + ' GW'))
print ('max solar = ' + str(format(max(solar_germany), '.2f') + ' GW'))
print ('max load = ' + str(format(max(load_germany), '.2f') + ' GW' + '\n'))
print ('wind ratio = ' + str(format(sum(wind_normalized)/sum(load_germany), '.2%')))
print ('solar ratio =' + str(format(sum(solar_germany)/sum(load_germany), '.2%')))
print ('gas ratio = ' + str(format(sum(gas)/sum(load_germany), '.2%')))
print ('li-ion ratio = x' + str(format((sum(charged)/capacity), '.2f')) + '\n')
average_load = format(sum(load_germany)/int(len(load_germany)), '2f')
print ('average load = ' + str(average_load) + ' GW')
