#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv

# входные данные, помимо входного CSV

scenarios_number = 2 # сколько сценариев анализировать
hours_to_analyze = 190 * 24 # cколько часов (строк) анализировать

wind_multiplier = [2.5, 3] # во сколько раз увеличить модельную (равномерную по 4-м странам) генерацию ветра Германии. Первое значение для первого сценария и так далее.
solar_multiplier = [3, 4] # во сколько раз увеличить реальную генерацию солнца Германии
capacity_storage = [650, 1300] # ёмкость аккумуляции в ГВт*ч. 1300 ГВт*ч эквивалентно суточному потреблению.

# LCOE

lcoe_wind = [70, 80] 
lcoe_solar = [80, 90]
lcoe_gas = [70, 90]

# переменные вычисления LCOE хранения

price_kwh_storage = [100, 150] # цена системы хранения э/э за кВт*ч
discount_rate_storage = 1.045 # процент по кредиту
years_storage = 15 # срок кредита

# работа с CSV

csv_input_file = 'wind-4norm-solar-load.csv' # Имя файла с вводными данными. Формат столбцов: ветер в Германии, нормировка ветра на 4 страны, солнце в Германии, загрузка в Германии. Хранить в том же каталоге.
csv_output_files = ['output7.csv', 'output8.csv']
csv_summary = 'summary.csv'
col_delimiter='\t' # делимитер для CSV файла

# объявление массивов входных данных

wind_germany = [0] * hours_to_analyze
wind_normalized = [0] * hours_to_analyze
load = [0] * hours_to_analyze
solar = [0] * hours_to_analyze

# объявление массивов анализируемых данных

accumulated = [0] * hours_to_analyze
charged = [0] * hours_to_analyze
discharged = [0] * hours_to_analyze
gas = [0] * hours_to_analyze
overhead = [0] * hours_to_analyze
inbattery_list = [0] * hours_to_analyze

i = 0
summary = []

# cчитать CSV-файл в массив нужной длины

with open(csv_input_file, 'rb') as input_file:
    input = csv.reader(input_file, delimiter = col_delimiter)
    for row in input:
        wind_germany[i], wind_normalized[i], solar[i], load[i] = row
        load[i] = float(load[i])
        i = i + 1
        if i == hours_to_analyze :
            break

input_file.close()

# функция округления

def float_to_str (input, type):
    output = str(format(input, '.1f'))
    if type == 'gw' :
        output = output + ' GW'
    if type == 'percent':
        output = output + '%'
    return output

# функция вычисления всего и вся

def scenarios (j) :
    
    inbattery = 0
    result_function = []
    overhead_count = 0
    scenario_summary = []
    
    # формирование основного массива результатов
    
    for i in range(hours_to_analyze) :
        wind_normalized[i] = float(wind_normalized[i]) * wind_multiplier[j]
        solar[i] = float(solar[i]) * solar_multiplier[j]
    
        if load[i] > wind_normalized[i] + solar[i]:      # если идёт разрядка
            if load[i] - wind_normalized[i] - solar[i] < inbattery :     # если в батарее достаточно ээ, то вычисляем сколько нужно и вычитаем
                discharged[i] = load[i] - (wind_normalized[i] + solar[i])
                inbattery = inbattery - discharged[i]      # вычисляем новый уровень батареи
                inbattery_list[i] = inbattery
         
            else:       # если в батарее недостаточно ээ, то
                discharged[i] = inbattery
                inbattery = 0
                gas[i] = load[i] - (wind_normalized[i] + solar[i]) - discharged[i]
                inbattery_list[i] = inbattery
         
        else:         # идёт зарядка
            if wind_normalized[i] + solar[i] - load[i] < capacity_storage[j] - inbattery :     # если в аккуме хватает места
                charged[i] = wind_normalized[i] + solar[i] - load[i]
                inbattery = inbattery + wind_normalized[i] + solar[i] - load[i]
                inbattery_list[i] = inbattery
         
            else:          # если в аккуме не хватает места
                charged[i] = capacity_storage[j] - inbattery
                inbattery = capacity_storage[j]
                overhead[i] = wind_normalized[i] + solar[i] - load[i] - charged[i]
                inbattery_list[i] = inbattery
                overhead_count = overhead_count + 1
   
        i = i + 1
    
    # запись рассчитанных почасовых данных в CSV файл

    with open(csv_output_files[j], 'wb') as output_file:
        write = csv.writer(output_file)
        rows = zip(wind_normalized, solar, load, charged, discharged, inbattery_list, overhead, gas)
        title = ['wind_normalized', 'solar', 'load', 'charged', 'discharged', 'inbattery', 'overhead', 'gas']
        write.writerow(title)
        
        i = 0
        for row in rows:
            write.writerow(row)
            if i == hours_to_analyze :
                break
            i = i + 1
            
    output_file.close()
    
    # расчёт и возврат кратких выводов
    
    storage_utilization = float_to_str((sum(charged) / capacity_storage[j]), 'nothing')
    average_load = float_to_str(sum(load) / len(load), 'gw')
    
                      # расчёт LCOE
    
    lcoe_storage = price_kwh_storage[j] * 1000 * pow(discount_rate_storage, years_storage) / (sum(charged) / capacity_storage[j] * years_storage)
    lcoe = (sum(wind_normalized) * lcoe_wind[j] + sum(solar) * lcoe_solar[j] + sum(gas) * lcoe_gas[j] + sum(discharged) * lcoe_storage)/sum(load)
    lcoe_without_storage = (sum(wind_normalized) * lcoe_wind[j] + sum(solar) * lcoe_solar[j] + sum(gas) * lcoe_gas[j]) / sum(load)
    
                      # округление LCOE
    
    lcoe_storage = float_to_str(lcoe_storage, 'nothing')
    lcoe = float_to_str(lcoe, 'nothing')
    lcoe_without_storage = float_to_str(lcoe_without_storage, 'nothing')
    
                      # остальные расчёты и округления
    
    overhead_count = str(overhead_count) + ' Hours'
    max_overhead = float_to_str(max(overhead), 'gw')
    max_gas = float_to_str(max(gas), 'gw')
    max_wind = float_to_str(max(wind_normalized), 'gw')
    max_solar = float_to_str(max(solar), 'gw')
    max_load = float_to_str(max(load), 'gw')
    wind_ratio = float_to_str(sum(100 * wind_normalized)/sum(load), 'percent')
    solar_ratio = float_to_str(sum(100 * solar)/sum(load), 'percent')
    gas_ratio = float_to_str(100 * sum(gas)/sum(load), 'percent')
    storage_ratio = float_to_str(100 * sum(charged) / sum(load), 'percent')
    
    # формирование массива кратких результатов

    scenario_summary = ['scenario ' + str((j+1)), storage_utilization, average_load, lcoe_storage,
                        lcoe, lcoe_without_storage, overhead_count, max_overhead, max_gas, max_wind,
                        max_solar, max_load, wind_ratio, solar_ratio, gas_ratio, storage_ratio]
    return scenario_summary
    

# запуск функции

i = 0
summary.append([' ', 'storage cycles', 'average_load', 'lcoe_storage', 'lcoe', 'lcoe_without_storage',
                'overhead_count', 'max_overhead', 'max_gas', 'max_wind', 'max_solar', 'max_load',
                'wind_ratio', 'solar_ratio', 'gas_ratio', 'storage_ratio']) #    формирование заголовков строк для кратких выводов

for i in range(scenarios_number) : #     цикл по сценариям
    summary.append(scenarios(i)) #      запись кратких итогов в массив

summary = map(list, zip(*summary))     # транспонирование таблицы кратких итогов
    
print ('summary = ', summary)


# запись кратких итогов разных сценариев в файл 

i = 0
with open(csv_summary, 'wb') as summary_file:
    write = csv.writer(summary_file)
    write.writerows(summary)
        
summary_file.close()