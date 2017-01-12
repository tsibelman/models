 #! /usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib # импорт библиотеки рисования графика
matplotlib.use('agg')
import matplotlib.pyplot as plt
from functions import read_csv, draw_chart, generate_date_range # импорт функции read_csv из файла functions.py

def production_model(extrapolation_range, ignore_productivity, *args) : #      рассчитывает
    
    #plt.figure()
    #plt.grid(True)
    fig = plt.figure(figsize=(10,15))
   # plt.set_figheight(100)
    #plt.grid(True)
    #fig.grid()
    chart1 = fig.add_subplot(311)
    chart1.grid()
    chart2 = fig.add_subplot(312)
    chart2.grid()
    chart3 = fig.add_subplot(313)
    chart3.grid()
    cycle = False
    
    for rig_ratio in args :
        rig_count, rig_productivity = read_csv('dpr_rigs_and_productivity.csv', 2)
        input_length = len(rig_count) - 1     # переменная для длины массива
        print ('rig_ratio = ', rig_ratio)
        
        production_matrix = []
        zeroes = []
        well_profile = []
        production = []
        new_production = []
        production_denom_m = []
        production_denom_t = []
        production_forecast_for_chart = [0] * 2 * extrapolation_range
        rigs_forecast_for_chart = [0] * 2 * extrapolation_range
        new_production_forecast_4chart = [0] * 2 * extrapolation_range
        old_production_decline_forecast_4chart = [0] * 2 * extrapolation_range

        
        production_for_chart = [0] * (input_length + 1)
        rigs_for_chart = [0] * (input_length + 1)
        new_production_4chart = [0] * (input_length + 1)
        old_production_decline_4chart = [0] * (input_length + 1)

        row_matrix = []
        old_production_decline = [0] * (input_length + 2 * extrapolation_range)
        i = 0
        j = 0
    
    # всё что нужно для экстраполяции буровых и продуктивности
        
        rig_count_end_value = max(rig_count) * rig_ratio                                                           # вычисление последнего прогнозируемого количества буровых
        rig_count_step = (rig_count_end_value - rig_count[input_length]) / (extrapolation_range * 1.0)     # вычисление шага изменения буровых в прогнозе
        rig_productivity_coefficient = 2.5 / ((rig_count_end_value / rig_count[input_length]) + 1.5)                # вычисление изменение продуктивности буровых в зависимости от количества
        rig_productivity_end_value = rig_productivity[input_length] * rig_productivity_coefficient                  # вычисление последней прогнозируемой эффективности буровых
        rig_productivity_step = (rig_productivity_end_value - rig_productivity[input_length]) / extrapolation_range # вычисление шага продуктивности в прогнозе
        
        print (rig_count_end_value)
        print (rig_count_step)
        print (rig_productivity_coefficient)
        print (rig_productivity_end_value)
        print (rig_productivity_step)
    
    # вычисление коэффициентов для профиля скважин
    
        for i in range(input_length + 2 * (extrapolation_range + 75)) :
         well_profile.append(1 / ((1 + 0.15 * i) ** 0.98))   
    
    # экстраполяция буровых и продуктивности
    
        for i in range(2 * extrapolation_range):     # цикл по базовым начальным данным
            if i < extrapolation_range :    # дописать в массив прогнозные значения для буровых и их продуктивности
                rig_count.append(rig_count[input_length] + rig_count_step * (i + 1))
                if ignore_productivity == True :
                     rig_productivity.append(rig_productivity[input_length])
                else :
                    rig_productivity.append(rig_productivity[input_length] + rig_productivity_step * (i + 1))
            else :
                rig_count.append(rig_count[input_length + extrapolation_range])
                rig_productivity.append(rig_productivity[input_length + extrapolation_range])
    
    # формирование массива добычи до начала ведения статистики EIA DPR (0,4 МБ/д на 2007 год)
    
        for i in range(input_length + 2 * extrapolation_range) :
            row_matrix.append(405891 * well_profile[i + 75] * 11)
            new_production.append(rig_count[i] * rig_productivity[i] / 1000)     # вычисление ввода добычи
    
    # создание первой строки в матрице добычи - остаток от начальных 0,4 МБ/д в 2007 году.
        production_matrix.append(row_matrix)
    
    
        for i in range(input_length + 2 * extrapolation_range):    # формирование матрицы добычи по месяцам и по группам скважин 
            row_matrix = []      # обнуляем динамику добычи месячных скважин
        
            if i >= 1: zeroes.append(0)      # добавляем i нулей в начало строки добычи
            row_matrix.extend(zeroes)

            for j in range(input_length + 2 * extrapolation_range):

                row_matrix.append(rig_count[i] * rig_productivity[i] * well_profile[j])
      
            production_matrix.append(row_matrix)

        matrix_transposed = map(list, zip(*production_matrix))
    
        for i in range(input_length + 2 * extrapolation_range) :      # вычисление добычи, в т.ч. деноминированной и снижения старой добычи.
            production.append(sum(matrix_transposed[i]))
            production_denom_m.append(sum(matrix_transposed[i])/1000000)
            production_denom_t.append(sum(matrix_transposed[i])/1000)
        
            if i != 0 :
                old_production_decline[i] = new_production[i] - (production_denom_t[i] - production_denom_t[i-1])
        old_production_decline[0] = old_production_decline[1]    # костыль для отсутствующего первого значения снижения старой добычи
    
        for i in range (input_length + 1) : # сохранение добычи в подходящий по размеру для графика массив
            production_for_chart[i] = production_denom_m[i]
            rigs_for_chart[i] = rig_count[i]
            new_production_4chart[i] = new_production[i]
            old_production_decline_4chart[i] = old_production_decline[i]


        for i in range (2 * extrapolation_range) : #сохранение прогноза добычи в подходящий по размеру для графика массив
            production_forecast_for_chart[i] = production_denom_m[i + input_length]
            #print i
            rigs_forecast_for_chart[i] = rig_count[i + input_length]
            new_production_forecast_4chart[i] = new_production[i + input_length]
            old_production_decline_forecast_4chart[i] = old_production_decline[i + input_length]
        
        dates_main = generate_date_range('2007-01-01', input_length + 1)
        dates_forecast = generate_date_range('2017-01-01', 2 * extrapolation_range)
        dates_all = generate_date_range('2007-01-01', (input_length + 1) + 2 * extrapolation_range) 
        
        if cycle == False :
            chart1.plot(dates_main, production_for_chart) # рисование графика
            chart2.plot(dates_main, rigs_for_chart)
            chart3.plot(dates_main, new_production_4chart)
            
        chart1.plot(dates_forecast, production_forecast_for_chart, ':')
        chart2.plot(dates_forecast, rigs_forecast_for_chart, ':')
        chart2.set_ylim(ymin = 0)
        chart3.plot(dates_forecast, new_production_forecast_4chart)
        
        
        cycle = True
        
    plt.savefig('chart1.png') # сохранение нарисованного графика в файл
        
production_model(20, False, 0.28, 0.5)





    
        #draw_chart('chart.png', dates_main, dates_forecast, production_for_chart, production_forecast_for_chart)
    
    # тут надо рисовать график и видимо не функцией
    
    #return input_length, production_denom_m, new_production, old_production_decline, rig_count, rig_productivity, production_for_chart, production_forecast_for_chart

#production1, new_production1, old_production_decline1, rig_count1, rig_productivity1 = production_forecast(0.4, 36)

#forecast_range = 20
#def production_model(extrapolation_range, ignore_productivity, *args) : #      рассчитывает

#csv_length2, production2, new_production2, old_production_decline2, rig_count2, rig_productivity2, production2, production_forecast2 = production_model(0.20, forecast_range, False)
#draw_chart('chart.png', dates_main, dates_forecast, production1, production_forecast1, production_forecast2)
#draw_chart(dates_forecast, new_production2, old_production_decline2, 'chart3.png')
#draw_chart(dates_all, dates_all, rig_count2, rig_productivity2, rig_productivity2, 'chart5.png')