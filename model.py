#! /usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib  # импорт библиотеки рисования графика
from functions import read_csv, generate_date_range  # импорт функций из файла functions.py

matplotlib.use('agg')

# основная функция. принимает на вход период экстраполяции, учитывать ли изменение продуктивности буровых
# и любое количество сценариев изменения буровых, где 1 = докризисный максимум буровых. Сначала в период экстраполяции
# буровые растут до поданного на вход значения, потом ещё один период буровые стагнируют


def production_model(extrapolation_range, ignore_productivity, *args):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10, 15))
    chart1 = fig.add_subplot(311)
    chart1.grid()
    chart2 = fig.add_subplot(312)
    chart2.grid()
    chart3 = fig.add_subplot(313)
    chart3.grid()
    cycle = False  # метка прохождения первого цикла

    rig_count_saved, rig_productivity_saved = read_csv('data/dpr_rigs_and_productivity.csv', 2)  # чтение csv
    input_length = len(rig_count_saved) - 1  # переменная для длины массива

    # создание профиля скважин (нормирован к 1)
    well_profile = []
    for i in range(input_length + 2 * extrapolation_range + 75):
        well_profile.append(1 / ((1 + 0.15 * i) ** 0.98))

    # цикл по сценариям буровых из аргументов функции
    for rig_ratio in args:

        rig_count = list(map(int,rig_count_saved))
        rig_productivity = list(map(int,rig_productivity_saved))

        production_matrix = []
        production = []  # добыча
        new_production = []  # ввод добычи
        old_production_decline = [0] * (input_length + 2 * extrapolation_range)

        # всё что нужно для линейной экстраполяции буровых (из аргументов функции) и продуктивности
        rig_count_end_value = max(rig_count) * rig_ratio  # вычисление последнего прогнозируемого количества буровых
        rig_count_step = (rig_count_end_value - rig_count[input_length]) / (extrapolation_range * 1.0)  # вычисление шага изменения буровых в прогнозе
        rig_productivity_coefficient = 2.5 / ((rig_count_end_value / rig_count[input_length]) + 1.5)  # вычисление изменение продуктивности буровых в зависимости от количества
        rig_productivity_end_value = rig_productivity[input_length] * rig_productivity_coefficient  # вычисление последней прогнозируемой эффективности буровых
        rig_productivity_step = (rig_productivity_end_value - rig_productivity[input_length]) / extrapolation_range  # вычисление шага продуктивности в прогнозе

        # экстраполяция буровых и продуктивности
        for i in range(2 * extrapolation_range):  # цикл по базовым начальным данным
            if i < extrapolation_range:  # дописать в массив прогнозные значения для буровых и их продуктивности
                rig_count.append(rig_count[input_length] + rig_count_step * (i + 1))
                if ignore_productivity:
                    rig_productivity.append(rig_productivity[input_length])
                else:
                    rig_productivity.append(rig_productivity[input_length] + rig_productivity_step * (i + 1))
            else:
                rig_count.append(rig_count[input_length + extrapolation_range])
                rig_productivity.append(rig_productivity[input_length + extrapolation_range])

        row_matrix = []
        # формирование массива добычи до начала ведения статистики EIA DPR (0,4 МБ/д на 2007 год)
        for i in range(input_length + 2 * extrapolation_range):
            row_matrix.append(405891 * well_profile[i + 75] * 11)
            new_production.append(rig_count[i] * rig_productivity[i] / 1000)  # вычисление ввода добычи

        # создание первой строки в матрице добычи - остаток от начальных 0,4 МБ/д в 2007 году.
        production_matrix.append(row_matrix)

        # формирование матрицы добычи по месяцам и по группам скважин
        for i in range(input_length + 2 * extrapolation_range):
            row_matrix = [0] * i
            rigs_productivity = rig_count[i] * rig_productivity[i]
            for j in range(input_length + 2 * extrapolation_range):
                row_matrix.append( rigs_productivity * well_profile[j])
            production_matrix.append(row_matrix)

        # вычисление добычи
        matrix_transposed = list(map(list, zip(*production_matrix)))
        for mont_prod in matrix_transposed:
            production.append(sum(mont_prod))

        for i in range(input_length + 2 * extrapolation_range):
            if i != 0:
                old_production_decline[i] = new_production[i] - (production[i] - production[i - 1]) / 1000
        # поправка для отсутствующего первого значения снижения старой добычи
        old_production_decline[0] = old_production_decline[1]


        production_denom_m = [x / 1000000 for x in production]
        dates_main = generate_date_range('2007-01-01', input_length + 1)
        if not cycle:  # рисование модельных данных без прогноза
            chart1.plot(dates_main, production_denom_m[:input_length + 1])
            chart2.plot(dates_main, rig_count[:input_length+1])
            chart3.plot(dates_main, new_production[:input_length + 1])
            chart3.plot(dates_main, old_production_decline[:input_length + 1])

        # рисование прогнозов
        dates_forecast = generate_date_range('2017-01-01', 2 * extrapolation_range)
        chart1.plot(dates_forecast, production_denom_m[input_length:], ':')
        chart2.plot(dates_forecast, rig_count[input_length+1:], ':')
        chart2.set_ylim(ymin=0)  # ордината от нуля
        chart3.plot(dates_forecast, new_production[input_length:])
        chart3.plot(dates_forecast, old_production_decline[input_length:], ':')

        cycle = True  # метка первого прохода цикла

    plt.savefig('chart1.png')  # сохранение нарисованного графика в файл

production_model(20, False, 0.1, 0.4)

