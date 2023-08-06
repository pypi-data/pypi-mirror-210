'''
Authors: Luiz Gustavo Mugnaini Anselmo (nUSP: 11809746)
         Victor Manuel Dias Saliba     (nUSP: 11807702)
         Luan Marc Suquet Camargo      (nUSP: 11809090)

Computacao III (CCM): EP 1
Dekker method for finding roots of a given function.
'''
from numerical.roots.dekker import dekker


def main():
    '''Interactive test for the Dekker method'''
    st = input('Which function would you like to use? '
               '(Use x as a variable, ex: x ** 2 - 3):\n')
    f = lambda x: eval(st)
    a = float(input('Head of the interval: '))
    b = float(input('Tail of the interval: '))
    abs_error = float(input('Absolute error: '))
    rel_error = float(input('Relative error: '))
    dekker(f, a, b, abs_error, rel_error)


if __name__ == '__main__':
    main()
