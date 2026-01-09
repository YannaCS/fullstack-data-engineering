# LIST - array - mutable

numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# read by index
print(numbers[1])
# print(numbers[len(numbers) - 1])
print(numbers[-1])


print(len(numbers))

# basic slice
print(numbers[2:5])
print(numbers[:3])
print(numbers[3:])

# search
print(5 in numbers)
print(10 in numbers)

# careful the out of range indexing
# print(numbers[11])


# Advanced slice

print(numbers[::2])
print(numbers[::-1])
print(numbers[2::3])
print(numbers[::-2])

# List methods

# append - add element
numbers = [1, 2, 3]
numbers.append(4)
print(numbers)
numbers.append([5, 6])
print(numbers)

# extend - add multiple elements
numbers = [1, 2, 3]
numbers.extend([4, 5])
print(numbers)
print([1, 2, 3] + [4, 5] + [6, 7])
numbers.extend('ab')
print(numbers)

# insert element
numbers = [1, 2, 3]
numbers.insert(0, 0)  # [0, 1, 2, 3]
print(numbers)
numbers.insert(1, 999)
print(numbers)

# remove element
numbers = [1, 2, 2, 3]
numbers.remove(3)
print(numbers)

# pop
numbers = [1, 2, 3]
last = numbers.pop()
print(last, numbers)

# reverse
numbers = [1, 2, 3]
numbers.reverse()
print(numbers)

# sort
numbers = [4, 1, 5, 2, 1]

# in-place sorting
# numbers.sort()
# print(numbers)

print(sorted(numbers), numbers)

# combine multiple array
array_1 = [1, 2, 3]
array_2 = [4, 5, 6]
array_3 = [7, 8, 9]

combined = [*array_1, *array_2, *array_3]
print(combined)

# list unpack
numbers = [1, 2, 3]
num_1, num_2, num_3 = numbers
print(num_1, num_2, num_3)

# gather
numbers = [1, 2, 3, 4, 5]
num_1, *middle, num_last = numbers
print(num_1, num_last, middle)

numbers = [1, 2, 3]
num_1, num_2, _ = numbers
print(num_1, num_2)

# Pythonic
# List Comprehension
numbers = []
for i in range(10):
    numbers.append(i**2)

print(numbers)

# simple comprehension
squares = [i**2 for i in range(10)]
print(squares)

# with condition

evens = [n for n in range(10) if n % 2 == 0]
print(evens)

# With if-else
labels = ['even' if n % 2 == 0 else 'odd' for n in range(10)]
print(labels)

# nested comprehension
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
print(flat)
