#! /usr/bin/env python
# -*- coding: utf-8 -*-

from functions import read_csv, draw_chart, generate_date_range # импорт функции read_csv из файла functions.py

def production_forecast(rig_ratio, extrapolation_range, ignore_productivity) : #      рассчитывает
    
    rig_count, rig_productivity = read_csv('dpr_rigs_and_productivity.csv', 2)
    
    production = 0
    production_matrix = []
    zeroes = []
    well_profile = []
    massiv_new_wells = []
    production = []
    new_production = []
    production_denom_m = []
    production_denom_t = []
    row_matrix = []
    input_length = len(rig_count) - 1     # переменная для обращения к последнему элементу массива

    old_production_decline = [0] * (input_length + 2 * extrapolation_range)
    
    rig_count_end_value = max(rig_count) * rig_ratio        # вычисление последнего прогнозируемого количества буровых
    #if rig_ratio == 0 :
    #    rig_count_step = 0
    #else :
    rig_count_step = ((max(rig_count) * rig_ratio) - rig_count[input_length]) / (extrapolation_range * 1.0)       # вычисление шага изменения буровых в прогнозе
    print ('!!! extrapolation_range = ', extrapolation_range)
    #rig_productivity_coefficient = (0.11 * (-1) * (rig_count_end_value / rig_count[input_length])) + 1.3
    #rig_productivity_coefficient = 1.8 * ((0.05 * (rig_count_end_value / rig_count[input_length]) + 1) ** (-7))
    rig_productivity_coefficient = 2.5 / ((rig_count_end_value / rig_count[input_length]) + 1.5)
    rig_productivity_end_value = rig_productivity[input_length] * rig_productivity_coefficient      # вычисление последней прогнозируемой эффективности буровых
    rig_productivity_step = (rig_productivity_end_value - rig_productivity[input_length]) / extrapolation_range #      вычисление шага продуктивности в прогнозе
    
    print ('rigs_now = ', rig_count[input_length])
    print ('rigs_max = ', max(rig_count))
    print ('rigs_end_value = ', rig_count_end_value)
    print ('rig_ratio = ', rig_ratio)
    print ('rig_count_step = ', rig_count_step)
    print (' ')
    

    print ('rig_productivity_now = ', rig_productivity[input_length])
    print ('rig_productivity_coefficient = ', rig_productivity_coefficient)
    print ('rig_productivity_end_value = ', rig_productivity_end_value)
    print ('rig_productivity_step = ', rig_productivity_step)
    print (' ')
    
    for i in range(input_length + 2 * (extrapolation_range + 75)) :
         well_profile.append(1 / ((1 + 0.15 * i) ** 0.98))
    
    for i in range(input_length + 2 * extrapolation_range):     # цикл по базовым начальным данным
        if i < extrapolation_range :    # дописать в массив прогнозные значения для буровых и их продуктивности
             rig_count.append(rig_count[input_length] + rig_count_step * (i + 1))
             if ignore_productivity == True :
                 rig_productivity.append(rig_productivity[input_length])
             else :
                 rig_productivity.append(rig_productivity[input_length] + rig_productivity_step * (i + 1))
             
             #print ('rigs = ', rig_count[input_length + i], i)
    
    
    for i in range(extrapolation_range):
        rig_count.append(rig_count[input_length + extrapolation_range])
        rig_productivity.append(rig_productivity[input_length + extrapolation_range])
    print ('rigs = ', rig_count)
           
    for i in range(input_length + 2 * extrapolation_range):    #   формирование массива добычи до начала ведения статистики EIA DPR (0,4 МБ/д на 2007 год)
        row_matrix.append(405891 * well_profile[i + 75] * 11)
        new_production.append(rig_count[i] * rig_productivity[i] / 1000)     # вычисление ввода добычи
    
    production_matrix.append(row_matrix)
    
    
    for i in range(input_length + 2 * extrapolation_range):    # формирование матрицы добычи по месяцам и по группам скважин
            #rig_count.append(150)
            #rig_productivity.append(rig_productivity[input_length])
            #rig_count.append(rig_count[input_length])    
        row_matrix = []      # обнуляем динамику добычи месячных скважин
        
        if i >= 1: zeroes.append(0)      # добавляем i нулей в начало строки добычи
        row_matrix.extend(zeroes)

        for j in range(input_length + 2 * extrapolation_range):

            row_matrix.append(rig_count[i] * rig_productivity[i] * well_profile[j])
      
        production_matrix.append(row_matrix)

    matrix_transposed = map(list, zip(*production_matrix))
    https://vk.com/id266233524
    for i in range(input_length + 2 * extrapolation_range) :      # вычисление добычи, в т.ч. деноминированной и снижения старой добычи.
        production.append(sum(matrix_transposed[i]))
        production_denom_m.append(sum(matrix_transposed[i])/1000000)
        production_denom_t.append(sum(matrix_transposed[i])/1000)
        
        if i != 0 :
            old_production_decline[i] = new_production[i] - (production_denom_t[i] - production_denom_t[i-1])
    old_production_decline[0] = old_production_decline[1]    # костыль для отсутствующего первого значения снижения старой добычи
    
    return production_denom_m, new_production, old_production_decline, rig_count, rig_productivity

#production1, new_production1, old_production_decline1, rig_count1, rig_productivity1 = production_forecast(0.4, 36)
production2, new_production2, old_production_decline2, rig_count2, rig_productivity2 = production_forecast(0.28, 100, False)

a=[0]

dates1 = generate_date_range('2007-01-01', 320)
dates1 = generate_date_range('2007-01-01', 320)

#draw_chart(production1, production2, 'chart.png')
draw_chart(dates, production2, production2, 'chart.png')
#draw_chart(new_production1, old_production_decline1, 'chart2.png')
draw_chart(dates, new_production2, old_production_decline2, 'chart3.png')
#draw_chart(rig_count2, rig_productivity2, 'chart5.png')
#draw_chart(well_profile1, well_profile2, 'chart6.png')
print (production2[319] - production2[318])
print (production2[318] - production2[317])
print (production2[300] - production2[299])