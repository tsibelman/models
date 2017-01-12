matrix = []
y_divergence = []
y_results = []
y_sum = []
a_list = []
b_list = []
c_list = []
d_list = []
x = 0
xc = -2.5

for i in range(50) :
    a_list.append(x)
    b_list.append(x)
    c_list.append(xc)
    x = x + 0.1
    xc = xc + 0.1

x = 0
    
for i in range(10) :
    d_list.append(x)
    x = x + 0.1
    
x_list = [0.01,1,2,6]
y_target_list = [1.8, 1, 0.6, 0.35]

for a in a_list :
     for b in b_list :
         if b != 0 :
             for c in c_list :
                 for d in d_list :
                     y_results = []
                     row_matrix = []
                     y_divergence = []
                     abcd_values = [a, b, c, d]
                     row_matrix.extend(abcd_values)
                     i = 0
                     for x in x_list :
                         y = (a * b ** (-1) * 2.718 ** ((-1) * (x - c) ** 2 / b ** 2)) + d
                         y_divergence.append(y_target_list[i] - y)
                         i = i + 1
                     y_sum1 = abs(y_divergence[0]) + abs(y_divergence[1]) + abs(y_divergence[2]) + abs(y_divergence[3])
                     row_matrix.append(y_sum1)
                     matrix.append(row_matrix)

matrix_transposed = map(list, zip(*matrix))
print ('min = ', min(matrix_transposed[4]))
min_number = matrix_transposed[4].index(min(matrix_transposed[4]))
print (matrix[min_number])

