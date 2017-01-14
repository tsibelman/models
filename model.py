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
    historical_range = len(rig_count_saved) - 1
    model_range = historical_range + 2 * extrapolation_range

    # создание профиля скважин (нормирован к 1)
    well_profile = [1 / ((1 + 0.15 * x) ** 0.98) for x in range(model_range + 75)]

    # цикл по сценариям буровых из аргументов функции
    for rig_ratio in args:

        rig_counts = list(map(int, rig_count_saved))
        rig_productivity = list(map(int, rig_productivity_saved))

        last_count = rig_counts[-1]
        last_productivity = rig_productivity[-1]

        # всё что нужно для линейной экстраполяции буровых (из аргументов функции) и продуктивности
        rig_count_end_value = max(rig_counts) * rig_ratio  # вычисление последнего прогнозируемого количества буровых
        rig_count_step = (rig_count_end_value - last_count) / (extrapolation_range * 1.0)  # вычисление шага изменения буровых в прогнозе
        rig_productivity_step = 0
        if not ignore_productivity:
            rig_productivity_step = calculate_rig_productivity_step(extrapolation_range, last_count, last_productivity, rig_count_end_value)

        # экстраполяция буровых и продуктивности
        forecast_rigs, forecast_productivity=generate_forecast(extrapolation_range, last_count, last_productivity, rig_count_step, rig_productivity_step)
        rig_counts.extend(forecast_rigs)
        rig_productivity.extend(forecast_productivity)

        new_production = []  # ввод добычи
        row_matrix = []
        # формирование массива добычи до начала ведения статистики EIA DPR (0,4 МБ/д на 2007 год)
        for i in range(model_range):
            row_matrix.append(405891 * well_profile[i + 75] * 11)
            new_production.append(rig_counts[i] * rig_productivity[i] / 1000)  # вычисление ввода добычи

        # создание первой строки в матрице добычи - остаток от начальных 0,4 МБ/д в 2007 году.
        production_matrix = [row_matrix]

        # формирование матрицы добычи по месяцам и по группам скважин
        for i in range(model_range):
            row_matrix = [0] * i
            rigs_productivity = rig_counts[i] * rig_productivity[i]
            for j in range(model_range):
                row_matrix.append(rigs_productivity * well_profile[j])
            production_matrix.append(row_matrix)

        # вычисление добычи
        matrix_transposed = list(map(list, zip(*production_matrix)))
        production = [sum(month_prod) for month_prod in matrix_transposed]

        old_production_decline = [0] * model_range
        for i in range(1,model_range):
            old_production_decline[i] = new_production[i] - (production[i] - production[i - 1]) / 1000
        # поправка для отсутствующего первого значения снижения старой добычи
        old_production_decline[0] = old_production_decline[1]

        production_denom_m = [x / 1000000 for x in production]
        dates_main = generate_date_range('2007-01-01', historical_range + 1)
        if not cycle:  # рисование модельных данных без прогноза
            chart1.plot(dates_main, production_denom_m[:historical_range + 1])
            chart2.plot(dates_main, rig_counts[:historical_range+1])
            chart3.plot(dates_main, new_production[:historical_range + 1])
            chart3.plot(dates_main, old_production_decline[:historical_range + 1])

        # рисование прогнозов
        dates_forecast = generate_date_range('2017-01-01', 2 * extrapolation_range)
        chart1.plot(dates_forecast, production_denom_m[historical_range:], ':')
        chart2.plot(dates_forecast, rig_counts[historical_range+1:], ':')
        chart2.set_ylim(ymin=0)  # ордината от нуля
        chart3.plot(dates_forecast, new_production[historical_range:])
        chart3.plot(dates_forecast, old_production_decline[historical_range:], ':')

        cycle = True  # метка первого прохода цикла

    plt.savefig('chart1.png')  # сохранение нарисованного графика в файл


def generate_forecast(extrapolation_range, last_rig_count, last_rig_productivity, rig_count_step,
                      rig_productivity_step):
    forecast_rigs = []
    forecast_productivity = []

    # Фаза роста
    for i in range(extrapolation_range):  # цикл по базовым начальным данным
        forecast_rigs.append(last_rig_count + rig_count_step * (i + 1))
        forecast_productivity.append(last_rig_productivity + rig_productivity_step * (i + 1))

    last_rig_count = forecast_rigs[-1]
    last_rig_productivity = forecast_productivity[-1]

    # Фаза стабильного плато
    for i in range(extrapolation_range):  # цикл по базовым начальным данным
        forecast_rigs.append(last_rig_count)
        forecast_productivity.append(last_rig_productivity)

    return forecast_rigs,forecast_productivity


def calculate_rig_productivity_step(extrapolation_range, last_rig_count, last_rig_productivity, rig_count_end_value):
    coefficient = 2.5 / ((rig_count_end_value / last_rig_count) + 1.5)  # вычисление изменение продуктивности буровых в зависимости от количества
    return (last_rig_productivity * (coefficient - 1)) / extrapolation_range  # вычисление шага продуктивности в прогнозе


production_model(20, False, 0.1, 0.4)
