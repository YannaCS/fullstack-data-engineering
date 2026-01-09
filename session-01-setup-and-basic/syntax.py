# This is a comment

'''
Multi lines comment
or long string
Used for documenting
'''

# BASIC data types

# Number

# Integer
age = 25
number = -1
print(age)

# Float
price = 25.1
temp = 35.1

print(price)

# String
name = '"Steven"'
message = "'Hello world'"
multi_line = """
this is a
multiline 
string
"""
print(name)
print(message)
print(multi_line)

# f-string
score = 95
score_str = f"Your score is: {score}"
print(score_str)

# Bool - Boolean
is_active = True
is_logged_in = False
is_expired = True

print(is_active and is_logged_in)
print(False and False)
print(True and True)
print(True or False)

print(not is_active) # False

# None - type
result = None

# type checking

print(type(score))
print(type(name))
print(type(price))
print(type(is_active))

# number operation
a = 10
b = 3

addition = a + b # 13
substraction = a - b #7
mutilply = a * b # 30
division = a / b 
floor_division = a // b
print(division)
print(floor_division)
mod = a % b
exponentiation = a ** b # 1000
print(mod)
print(exponentiation)

# comparison
x = 5
y = 10

print(x == y)
print(x != y)
print(x < y)
print(x > y)
print(x <= y)
print(x >= y)
print(x > 3 and x < 10)
print(3 < x < 10)

print(is_active is True) # singleton object
print(is_active is False)
print(result is None)

arr_1 = [1,2,3]
arr_2 = [1,2,3]

print(arr_1 == arr_2) # compare content
print(arr_1 is arr_2) # compare reference in memory

# best practice: use "==" for most of cases. Use "is" for singleton comparsion

# control flow
# condition: if-else-if
age = 18

if age < 13:
    print("child")
elif age < 20:
    print("teenager")
elif age < 60:
    print("Adult")
else:
    print('Senior')

if age < 20:
    status = "teenager"
else:
    status = "Adult"

# Tenary operation
status = "teenager" if age < 20 else "adult"
print(status)

# Nested condition
temperature = 25
is_raining = False

if temperature > 20:    
    if is_raining:
        print('warm but rainy')
    else:
        print('Warm and sunny')
else:
    print('Cold')

# Truthy & Flasy
my_str = ''
num = 0

# Falsy Value: False, None, "", [], {}, set(), tuple(), 0
if num == 0:
    print('truthy')
else:
    print('falsy')

# For loop
for i in range(5):
    if i == 3:
        continue
    print(f"Iteration: {i}")

    # if i == 3:
        # break

for i in range(1, 10, 2):
    print(i)

sports = ['footbal', 'basketball', 'baseball']

for sport in sports:
    print(sport)


for i, sport in enumerate(sports): # [index, value]
    print(f"sport: {sport} at {i}")


