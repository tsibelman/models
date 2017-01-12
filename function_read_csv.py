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
    
    if columns_to_return == 1 :
        return data[0]
    if columns_to_return == 2 :
        return data[0], data[1]
    if columns_to_return == 3 :
        return data[0], data[1], data[2]
    if columns_to_return == 4 :
        return data[0], data[1], data[2], data[3]
    if columns_to_return == 5 :
        return data[0], data[1], data[2], data[3], data[4]
    if columns_to_return == 6 :
        return data[0], data[1], data[2], data[3], data[4], data[5]
    if columns_to_return == 7 :
        return data[0], data[1], data[2], data[3], data[4], data[5], data[6]
    if columns_to_return == 8 :
        return data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]
    if columns_to_return == 9 :
        return data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]
    if columns_to_return == 10 :
        return data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9]
    if columns_to_return == 11 :
        return data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10]
    if columns_to_return == 12 :
        return data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]
    if columns_to_return == 13 :
        return data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[12]
    if columns_to_return == 14 :
        return data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[12], data[13]

def draw_chart(list_to_draw, png_filename) :
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    plt.plot(list_to_draw)
    plt.savefig(png_filename)