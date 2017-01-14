#! /usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib  # импорт библиотеки рисования графика
from functions import read_csv, generate_date_range  # импорт функций из файла functions.py


# основная функция. принимает на вход период экстраполяции, учитывать ли изменение продуктивности буровых
# и любое количество сценариев изменения буровых, где 1 = докризисный максимум буровых. Сначала в период экстраполяции
# буровые растут до поданного на вход значения, потом ещё один период буровые стагнируют
def production_model(extrapolation_range, ignore_productivity, rig_ratio):
    rig_saved, wells_per_rig_saved = read_csv('data/dpr_rigs_and_productivity.csv', 2)  # чтение csv
    historical_range = len(rig_saved) - 1
    model_range = historical_range + 2 * extrapolation_range

    # создание профиля скважин (нормирован к 1)
    well_profile = [1 / ((1 + 0.15 * x) ** 0.98) for x in range(model_range + 75)]

    # добычa до начала ведения статистики EIA DPR (0,4 МБ/д на 2007 год)
    prod_before_DPR = [405891 * well_profile[i + 75] * 11 for i in range(model_range)]

    rigs = list(map(int, rig_saved))
    wells_per_rig = list(map(int, wells_per_rig_saved))

    # всё что нужно для линейной экстраполяции буровых (из аргументов функции) и продуктивности
    last_rigs = rigs[-1]
    last_productivity = wells_per_rig[-1]
    rigs_target = max(rigs) * rig_ratio  # вычисление последнего прогнозируемого количества буровых
    rigs_step = (rigs_target - last_rigs) / extrapolation_range  # вычисление шага изменения буровых в прогнозе

    # экстраполяция буровых и продуктивности
    forecast_rigs, forecast_productivity = generate_forecast(extrapolation_range, last_rigs, last_productivity, rigs_step, rigs_target, ignore_productivity)
    rigs.extend(forecast_rigs)
    wells_per_rig.extend(forecast_productivity)

    # формирование матрицы добычи по месяцам и по группам скважин
    production_by_month = [prod_before_DPR]
    for m in range(model_range):
        new_wells = rigs[m] * wells_per_rig[m]
        row_matrix = [0] * m + [new_wells * well_profile[j] for j in range(model_range - m)]
        production_by_month.append(row_matrix)

    production = [sum(month_prod) for month_prod in zip(*production_by_month)]  # вычисление добычи

    new_production = [rigs[i] * wells_per_rig[i] / 1000 for i in range(model_range)]  # вычисление ввода добычи

    production_decline = [0] * model_range
    for i in range(1, model_range):
        production_decline[i] = new_production[i] - (production[i] - production[i - 1]) / 1000

    # поправка для отсутствующего первого значения снижения старой добычи
    production_decline[0] = production_decline[1]

    return production, rigs, new_production, production_decline, generate_date_range('2007-01-01',model_range), historical_range


def generate_forecast(extrapolation_range, last_rigs, last_productivity, rig_count_step, rigs_target, ignore_productivity):
    forecast_rigs = []
    forecast_productivity = []
    productivity_step = 0

    if not ignore_productivity:
        coefficient = 2.5 / (
        (rigs_target / last_rigs) + 1.5)  # вычисление изменение продуктивности буровых в зависимости от количества
        productivity_step = (last_productivity * (
        coefficient - 1)) / extrapolation_range  # вычисление шага продуктивности в прогнозе

    # Фаза роста
    for i in range(extrapolation_range):
        forecast_rigs.append(last_rigs + rig_count_step * (i + 1))
        forecast_productivity.append(last_productivity + productivity_step * (i + 1))

    last_rigs = forecast_rigs[-1]
    last_productivity = forecast_productivity[-1]

    # Фаза стабильного плато
    for i in range(extrapolation_range):
        forecast_rigs.append(last_rigs)
        forecast_productivity.append(last_productivity)

    return forecast_rigs, forecast_productivity


def draw_model():
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10, 15))
    chart1 = fig.add_subplot(311)
    chart1.grid()
    chart2 = fig.add_subplot(312)
    chart2.grid()
    chart3 = fig.add_subplot(313)
    chart3.grid()
    cycle = False  # метка прохождения первого цикла
    for rig_ratio in [0.1, 0.4]:
        production, rigs, new_production, production_decline, dates, historical_range = \
            production_model(20, False, rig_ratio)

        production_denom_m = [x / 1000000 for x in production]

        if not cycle:  # рисование модельных данных без прогноза
            historical_dates = dates[:historical_range + 1]
            chart1.plot(historical_dates, production_denom_m[:historical_range + 1])
            chart2.plot(historical_dates, rigs[:historical_range + 1])
            chart3.plot(historical_dates, new_production[:historical_range + 1])
            chart3.plot(historical_dates, production_decline[:historical_range + 1])

        # рисование прогнозов
        forecast_dates = dates[historical_range:]
        chart1.plot(forecast_dates, production_denom_m[historical_range:], ':')
        chart2.plot(forecast_dates, rigs[historical_range + 1:], ':')
        chart2.set_ylim(ymin=0)  # ордината от нуля
        chart3.plot(forecast_dates, new_production[historical_range:])
        chart3.plot(forecast_dates, production_decline[historical_range:], ':')

        cycle = True  # метка первого прохода цикла
    plt.savefig('chart1.png')  # сохранение нарисованного графика в файл


draw_model()
