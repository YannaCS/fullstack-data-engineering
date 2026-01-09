#implicit type conversion
num_int = 10 # int
num_float = 5.5 # float

result = num_int + num_float
print(result)
print(type(result))

# string to integer
age_str = "25"
age_int = int(age_str)
print(age_int, type(age_int))

number = 100
num_str = str(number)
print(type(num_str))

print(bool(number)) #true
print(bool(0)) #false
print(bool("")) #false

text = 'apple,banana,cherry'
fruits = text.split(',')
print(fruits)

list = ['apple', 'pear', 'cherry']
fruits_str = ",".join(list)
print(fruits_str)

char_str = "abc"
#res = int(char_str)
# be careful when convert str to number!!

