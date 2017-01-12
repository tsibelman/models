#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv

# входные данные, помимо входного CSV

hours_to_analyze = 360 * 24 # cколько часов (строк) анализировать
wind_multiply_number = 5 # во сколько раз увеличить модельную (равномерную по 4-м странам) генерацию ветра
solar_multiply_number = 1 # во сколько раз увеличить реальную генерацию солнца
capacity = 40 * 24 # ёмкость аккумуляции в ГВт*ч. 54*24 ГВт*ч эквивалентно суточному потреблению.
inbattery = 5000 # обнуление аккумулированной электроэнергии

lcoe_wind = 70 # LCOE
lcoe_solar = 80
lcoe_gas = 70

price_kwh_storage = 100 # цена системы хранения э/э за кВт*ч
discount_rate_storage = 1.045 # процент по кредиту
years_storage = 20 # срок кредита

# CSV

csv_input_file = 'wind-4norm-solar-load.csv' # Имя файла с вводными данными. Формат столбцов: ветер в Германии, нормировка на 4 страны, солнце в Германии, загрузка в Германии. Хранить в том же каталоге.
csv_output_file = "output8.csv"
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

overhead_count = 0 # обнуление счётчика превышений генерации над потреблением и аккумуляцией, то есть когда э/э больше, чем система может переварить

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

cycles_storage = sum(charged)/capacity
average_load = sum(load_germany)/int(len(load_germany))
lcoe_storage = price_kwh_storage * 1000 * pow(discount_rate_storage, years_storage) / (cycles_storage * years_storage)
lcoe = (sum(wind_normalized) * lcoe_wind + sum(solar_germany) * lcoe_solar + sum(gas) * lcoe_gas + sum(discharged) * lcoe_storage)/sum(load_germany)
lcoe_without_storage = ((sum(wind_normalized) * lcoe_wind + sum(solar_germany) * lcoe_solar + sum(gas) * lcoe_gas)/sum(load_germany))



print ('\n' + 'overhead count = ' + str(overhead_count) + ' Hours')
print ('max overhead = ' + str(int(max(overhead))) + ' GW' + '\n')
print ('max gas = ' + str(int(max(gas))) + ' GW')
print ('max wind = ' + str(int(max(wind_normalized))) + ' GW')
print ('max solar = ' + str(int(max(solar_germany))) + ' GW')
print ('max load = ' + str(int(max(load_germany))) + ' GW' + '\n')
print ('wind ratio = ' + str(int(sum(100 * wind_normalized)/sum(load_germany))) + '%')
print ('solar ratio =' + str(int(sum(100 * solar_germany)/sum(load_germany))) +'%')
print ('gas ratio = ' + str(int(100 * sum(gas)/sum(load_germany))) + '%')
print ('storage ratio = ' + str(int(100 * sum(charged) / sum(load_germany))) + '%')
print ('storage cycles = ' + str(int(cycles_storage)) + '\n')
print ('average load = ' + str(int(average_load)) + ' GW')
print ('lcoe storage = $' + str(int(lcoe_storage)))
print ('lcoe = $' + str(int(lcoe)))
print ('lcoe without storage = $' + str(int(lcoe_without_storage)))

