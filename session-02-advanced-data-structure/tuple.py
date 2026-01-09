# Tuple -immutable 
coordinates = (10, 20, 10, 30)

single_tuple = (5,)
empty = ()

print(single_tuple, type(single_tuple))
print(empty)

print(coordinates[1])

x, y, _, _ = coordinates
print(x)

# Only two methods
print(coordinates.count(10))
print(coordinates.index(30))



#difference with List
#Tuple:
#1. Immutable
#2. tuple fast
# 3. size is fixed
# 4. memory less
# 5. tuple can be key of dict, but list cannot
# 6. tuple : only two methods, List: many methods

#When to use
# Tuple: Fixed data
# List: Dynamic and many operation