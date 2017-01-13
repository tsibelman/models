#! /usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import pandas

import matplotlib  # импорт библиотеки рисования графика
matplotlib.use('agg')
import matplotlib.pyplot as plt


def read_csv(csv_input_filename, columns_to_return):  # формат вызова функции: имя файла, количество столбцов для вывода

    with open(csv_input_filename, 'rt') as input_file:
        data = list(csv.reader(input_file, delimiter='\t'))

    input_file.close()

    return tuple(map(list, zip(*data)))[:columns_to_return]


def draw_chart(x_list, list_to_draw1, list_to_draw2,png_filename):
    # на вход в функцию подаётся массив и имя файла, в который сохранить график

    plt.figure()
    plt.grid(True)
    plt.plot(x_list, list_to_draw1, ':')  # рисование графика
    plt.plot(x_list, list_to_draw2)
    plt.savefig(png_filename)  # сохранение нарисованного графика в файл


def generate_date_range(date_start, per):
    date_list = pandas.date_range(date_start, periods=per, freq='MS')
    # date_list = [d.strftime('%d.%m.%y') for d in pandas.date_range(date_start, date_end, freq = 'MS')]
    return date_list
