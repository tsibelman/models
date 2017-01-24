#! /usr/bin/env python
# -*- coding: utf-8 -*-

def read_csv(csv_input_filename, columns_to_return):  # формат вызова функции: имя файла, количество столбцов для вывода
    import csv
    with open(csv_input_filename, 'rt') as input_file:
        data = list(csv.reader(input_file, delimiter='\t'))

    input_file.close()
    return tuple(map(list, zip(*data)))[:columns_to_return]

def generate_date_range(date_start, per):
    import pandas
    date_list = pandas.date_range(date_start, periods=per, freq='MS')
    return date_list

def input_data() :
    rigs_scenarios_input = raw_input('Введите через пробел сценарии буровых в виде доли от исторического максимума (1018 шт). Десятичную часть отделять точкой. Например: 0.25 1.1\n')
    rigs_scenarios = rigs_scenarios_input.split()
    rigs_scenarios = list(map(float, rigs_scenarios))
    ignore_productivity = int(raw_input('Учитывать в прогнозе изменение продуктивности буровых в зависимости от их количества? 1 = да, 0 = нет.\n'))
    if ignore_productivity == 1 :
        ignore_productivity = False
    elif ignore_productivity == 0 :
        ignore_productivity = True
    else :
        print('Неверное значение')
        exit()
    extrapolation_range = int(raw_input('Вветиде срок прогноза в месяцах. Конечный сценарий будет включать удвоенный срок: сначала количество буровых изменяется до заданного значения, далее стагнирует.\n'))
    if extrapolation_range == 0 :
        print ('Срок прогнозирования должен быть отличен от нуля')
        exit()
    return rigs_scenarios, ignore_productivity, extrapolation_range

def production_model(extrapolation_range, ignore_productivity, rig_ratio):
    production_decline = []
    rig_saved, rig_productivity_saved, DPR_production = read_csv('data/dpr_rigs_and_productivity2.csv', 3)  # чтение csv
    historical_range = len(rig_saved) - 1
    model_range = historical_range + 2 * extrapolation_range + 1

    # создание профиля скважин (нормирован к 1)
    well_profile = [1 / ((1 + 0.15 * x) ** 0.98) for x in range(model_range + 75)]

    # добычa до начала ведения статистики EIA DPR
    prod_before_DPR = [400000 * well_profile[i + 30] * 5.18 for i in range(model_range)]

    rigs = list(map(int, rig_saved))
    rig_productivity = list(map(float, rig_productivity_saved))

    # всё что нужно для линейной экстраполяции буровых (из аргументов функции) и продуктивности
    last_rigs = rigs[-1]
    last_productivity = rig_productivity[-1]
    rigs_target = max(rigs) * rig_ratio  # вычисление последнего прогнозируемого количества буровых
    rigs_step = (rigs_target - last_rigs) / extrapolation_range  # вычисление шага изменения буровых в прогнозе

    # экстраполяция буровых и продуктивности
    forecast_rigs, forecast_productivity = generate_forecast(extrapolation_range, last_rigs, last_productivity, rigs_step, rigs_target, ignore_productivity, rig_productivity)
    rigs.extend(forecast_rigs)
    rig_productivity.extend(forecast_productivity)

    # формирование матрицы добычи по месяцам и по группам скважин
    production_by_month = [prod_before_DPR]
    for m in range(model_range):
        new_wells = rigs[m] * rig_productivity[m]
        row_matrix = [0] * m + [new_wells * well_profile[j] for j in range(model_range - m)]
        production_by_month.append(row_matrix)

    production = [sum(month_prod) for month_prod in zip(*production_by_month)]  # вычисление добычи

    new_production = [rigs[i] * rig_productivity[i] / 1000 for i in range(model_range)]  # вычисление ввода добычи
    new_production.append(new_production[-1])
    
    production_decline.append(0)

    for i in range(1, model_range):
        production_decline.append(new_production[i] - (production[i] - production[i - 1]) / 1000)
        if i == historical_range :
            production_decline.append(production_decline[-1])

    production_decline[0] = production_decline[1]
    #for n in range(model_range + 1) :
        #print (n, rigs[n], wells_per_rig[n], new_production[n], production_decline[n])
    return production, rigs, rig_productivity, new_production, production_decline, generate_date_range('2007-01-01', model_range), historical_range, DPR_production

def generate_forecast(extrapolation_range, last_rigs, last_productivity, rig_count_step, rigs_target, ignore_productivity, rig_productivity):
    forecast_rigs = []
    forecast_rigs.append(last_rigs)
    forecast_productivity = []
    forecast_productivity.append(last_productivity)
    productivity_step = 0
    
    if not ignore_productivity:
        for i in range(extrapolation_range):
            forecast_rigs.append(last_rigs + rig_count_step * (i + 1))
            forecast_productivity.append(345000 / (forecast_rigs[-1] + 200) + 150)
    else :
        for i in range(extrapolation_range):
            forecast_rigs.append(last_rigs + rig_count_step * (i + 1))
            forecast_productivity.append(forecast_productivity[-1])

    last_rigs = forecast_rigs[-1] # присваивание последнего значения массива
    last_productivity = forecast_productivity[-1]

    # Фаза стабильного плато
    for i in range(extrapolation_range):
        forecast_rigs.append(last_rigs)
        forecast_productivity.append(last_productivity)

    return forecast_rigs, forecast_productivity

def draw_model():
    import matplotlib  # импорт библиотеки рисования графика
    matplotlib.rc('font', family='DejaVu Sans') # шрифт с поддержкой русского языка
    matplotlib.use('agg') # при необходимости можно убрать для sagemath взамен %inline
    import matplotlib.pyplot as plt
    rigs_scenarios, ignore_productivity, extrapolation_range = input_data() # функция ввода данных с клавиатуры
    fig = plt.figure(figsize=(10, 15)) # создание рисунка размером 1000*1500 пикс. с графиками 
    chart1 = fig.add_subplot(411) # график и его расположение
    chart1.grid() # сетка для графика
    chart2 = fig.add_subplot(412)
    chart2.grid()
    chart3 = fig.add_subplot(413)
    chart3.grid()
    chart4 = fig.add_subplot(414)
    chart4.grid()
    i = 1 # переменная обозначения циклов
    for rig_ratio in rigs_scenarios: # цикл по сценариям буровых
        production, rigs, rig_productivity, new_production, production_decline, dates, historical_range, DPR_production = \
            production_model(extrapolation_range, ignore_productivity, rig_ratio)

        production_denom_m = [x / 1000000 for x in production]

        if i == 1:  # рисование модельных данных без прогноза
            historical_dates = dates[:historical_range + 1] # массив дат
            chart1.plot(historical_dates, production_denom_m[:historical_range + 1], label=u'Модель')
            chart1.plot(historical_dates, DPR_production[:historical_range + 1], label=u'Факт и модель EIA')
            chart2.plot(historical_dates, rigs[:historical_range + 1])
            #chart2.set_ylim(ymin=0)  # ордината от нуля
            chart3.plot(historical_dates, rig_productivity[:historical_range + 1])
            chart4.plot(historical_dates, new_production[:historical_range + 1], label=u'Новая')
            chart4.plot(historical_dates, production_decline[:historical_range + 1], label=u'Старая')

        # рисование прогнозов
        labels = u'сценарий %s' % i # переменная названия сценариев
        forecast_dates = dates[historical_range:] # массив дат
        chart1.plot(forecast_dates, production_denom_m[historical_range:], ':', label=labels)
        chart2.plot(forecast_dates, rigs[historical_range + 1:], ':', label=labels)
        
        chart3.plot(forecast_dates, rig_productivity[historical_range + 1:], ':', label=labels)
        chart4.plot(forecast_dates, new_production[historical_range + 1:], ':', label=labels)
        chart4.plot(forecast_dates, production_decline[historical_range + 1:], ':', label=labels)
        chart1.set_title(u'Добыча нефти НПК ("сланцевой")')
        chart2.set_title(u'Буровые в сланцевых мест-ях (с лагом в 2 месяца)')
        chart3.set_title(u'Продуктивность буровых')
        chart4.set_title(u'Ввод новой добычи и вывод старой')
        chart1.legend() # добавление и расположение легенд
        chart1.legend(loc='upper left')
        chart2.legend()
        chart2.legend(loc='upper left')
        chart3.legend()
        chart3.legend(loc='upper left')
        chart4.legend()
        chart4.legend(loc='upper left')
        i = i + 1
    #plt.show() # включить для sagemath и выключить строку ниже
    plt.savefig('chart2.png')   # сохранение нарисованного графика в файл
