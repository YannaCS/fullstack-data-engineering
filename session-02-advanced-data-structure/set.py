# Sets

fruits = {"apple", "Pear", "Cherry", "apple", 5}
empty = set()
print(empty)

print(fruits)

from_list = set([1,1,2,2,3,4])
print(from_list)

from_list.add(1)
from_list.add(5)
print(from_list)

a = {1,2,3,4}
b = {3,4,5,6}

#union
print( a | b )

#intersection
print(a & b)

#diff
print(a - b)

# symmtric diff - in a or b but not both

print(a ^ b)

#comprehension

squares = {x**2 for x in range(10)}
print(squares)



