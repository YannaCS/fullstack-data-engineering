import my_module

from my_module import greet, add
print(my_module.greet('Steven'))
print(my_module.add(1, 2))
print(my_module.PI)


print(greet('Steven 2'))
print(add(1, 3))

import my_module as mm

print(mm.greet('Steven'))


from my_module import greet as greet_func

print(greet_func('Adam'))

# from my_module import * # NOT RECOMMEND

# greet

if __name__ == '__main__':
    print('The main file is executed directly')
    print(greet_func('Adam'))