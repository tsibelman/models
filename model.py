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

    rig_saved, wells_per_rig_saved = read_csv('data/dpr_rigs_and_productivity.csv', 2)  # чтение csv
    historical_range = len(rig_saved) - 1
    model_range = historical_range + 2 * extrapolation_range

    # создание профиля скважин (нормирован к 1)
    well_profile = [1 / ((1 + 0.15 * x) ** 0.98) for x in range(model_range + 75)]

    # цикл по сценариям буровых из аргументов функции
    for rig_ratio in args:

        rigs = list(map(int, rig_saved))
        wells_per_rig = list(map(int, wells_per_rig_saved))

        last_rigs = rigs[-1]
        last_productivity = wells_per_rig[-1]

        # всё что нужно для линейной экстраполяции буровых (из аргументов функции) и продуктивности
        rigs_target = max(rigs) * rig_ratio  # вычисление последнего прогнозируемого количества буровых
        rigs_step = (rigs_target - last_rigs) / extrapolation_range   # вычисление шага изменения буровых в прогнозе
        productivity_step = 0
        if not ignore_productivity:
            productivity_step = calculate_rig_productivity_step(extrapolation_range, last_rigs, last_productivity, rigs_target)

        # экстраполяция буровых и продуктивности
        forecast_rigs, forecast_productivity=generate_forecast(extrapolation_range, last_rigs, last_productivity, rigs_step, productivity_step)
        rigs.extend(forecast_rigs)
        wells_per_rig.extend(forecast_productivity)

        # добычa до начала ведения статистики EIA DPR (0,4 МБ/д на 2007 год)
        prod_before_DPR = [405891 * well_profile[i + 75] * 11 for i in range(model_range)]

        # формирование матрицы добычи по месяцам и по группам скважин
        production_matrix = [prod_before_DPR]
        for m in range(model_range):
            new_wells = rigs[m] * wells_per_rig[m]
            row_matrix = [0] * m + [ new_wells * well_profile[j] for j in range(model_range-m)]
            production_matrix.append(row_matrix)

        production = [sum(month_prod) for month_prod in zip(*production_matrix)] # вычисление добычи

        new_production = [rigs[i] * wells_per_rig[i] / 1000 for i in range(model_range)] # вычисление ввода добычи

        old_production_decline = [0] * model_range
        for i in range(1,model_range):
            old_production_decline[i] = new_production[i] - (production[i] - production[i - 1]) / 1000
        # поправка для отсутствующего первого значения снижения старой добычи
        old_production_decline[0] = old_production_decline[1]

        production_denom_m = [x / 1000000 for x in production]
        dates = generate_date_range('2007-01-01', model_range)
        historical_dates = dates[:historical_range+1]
        if not cycle:  # рисование модельных данных без прогноза
            chart1.plot(historical_dates, production_denom_m[:historical_range + 1])
            chart2.plot(historical_dates, rigs[:historical_range+1])
            chart3.plot(historical_dates, new_production[:historical_range + 1])
            chart3.plot(historical_dates, old_production_decline[:historical_range + 1])

        # рисование прогнозов
        forecast_dates = dates[historical_range:]
        chart1.plot(forecast_dates, production_denom_m[historical_range:], ':')
        chart2.plot(forecast_dates, rigs[historical_range+1:], ':')
        chart2.set_ylim(ymin=0)  # ордината от нуля
        chart3.plot(forecast_dates, new_production[historical_range:])
        chart3.plot(forecast_dates, old_production_decline[historical_range:], ':')

        cycle = True  # метка первого прохода цикла

    plt.savefig('chart1.png')  # сохранение нарисованного графика в файл


def generate_forecast(extrapolation_range, last_rig_count, last_rig_productivity, rig_count_step,
                      rig_productivity_step):
    forecast_rigs = []
    forecast_productivity = []

    # Фаза роста
    for i in range(extrapolation_range):
        forecast_rigs.append(last_rig_count + rig_count_step * (i + 1))
        forecast_productivity.append(last_rig_productivity + rig_productivity_step * (i + 1))

    last_rig_count = forecast_rigs[-1]
    last_rig_productivity = forecast_productivity[-1]

    # Фаза стабильного плато
    for i in range(extrapolation_range):
        forecast_rigs.append(last_rig_count)
        forecast_productivity.append(last_rig_productivity)

    return forecast_rigs,forecast_productivity


def calculate_rig_productivity_step(extrapolation_range, last_rigs, last_productivity, rigs_target):
    coefficient = 2.5 / ((rigs_target / last_rigs) + 1.5)  # вычисление изменение продуктивности буровых в зависимости от количества
    return (last_productivity * (coefficient - 1)) / extrapolation_range  # вычисление шага продуктивности в прогнозе


production_model(20, False, 0.1, 0.4)