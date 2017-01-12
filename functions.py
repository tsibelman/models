#! /usr/bin/env python
# -*- coding: utf-8 -*-

def read_csv(csv_input_filename, columns_to_return) : #формат вызова функции: имя файла, количество столбцов для вывода
    
    import csv
    
    data = []
    col_delimiter='\t' # делимитер для CSV файла
    
    with open(csv_input_filename, 'rb') as input_file:
        input = csv.reader(input_file, delimiter = col_delimiter)
        i = 0
        for row in input :
            data.append(row)
            
    input_file.close()
    
    data = map(list, zip(*data))
    
    for i in range(len(data)) :
        data[i] = map(int, data[i])
    


def draw_chart(x_list, list_to_draw1, list_to_draw2, png_filename) : # на вход в функцию подаётся массив и имя файла, в который сохранить график
    import matplotlib # импорт библиотеки рисования графика
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    plt.figure()
    plt.grid(True)
    plt.plot(x_list, list_to_draw1, ':') # рисование графика
    plt.plot(x_list, list_to_draw2)
    plt.savefig(png_filename) # сохранение нарисованного графика в файл
    
def generate_date_range(date_start, per) :
    import pandas
    date_list = pandas.date_range(date_start, periods=per, freq='MS')
    #date_list = [d.strftime('%d.%m.%y') for d in pandas.date_range(date_start, date_end, freq = 'MS')]
    return date_list


