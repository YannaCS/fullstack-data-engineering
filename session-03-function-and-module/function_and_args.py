# function

# f(x, y) = 2x + y
# f(2,1) = 5
# f(10,5) = 25

def greet(name, age, title='Mr.'):  # with default argument
    return f"Hello, {title} {name} @ {age}"


# call the function
result = greet('Steven', "Dr.")
# print(result)

# key word arguments
print(greet('Steven', title="Dr.", age=25))

# Lambda function
# regular
def square(x):
    return x**2


# Lambda func (anonymous function)
lambda_square = lambda x: x**2


print(lambda_square(4))
def max_value(x, y): return x if x > y else y


print(max_value(10, 5))


numbers = [1, 2, 3, 4, 5]
print(list(map(square, numbers)))
print(list(map(lambda x: x**3, numbers)))
print(list(filter(lambda x: x % 2 == 0, numbers)))
# numbers -> map -> filter -> map

# multiple returns
def get_user_info():
    name = 'Steven'
    age = 25
    city = 'NYC'
    return name, age, city

name, age, city = get_user_info()
print(name, age, city)


# *args variable position args
def sum_all(*args):
    print(f"args: {args}")
    return sum(args)

print(sum_all(1, 2, 3, 4, 5, 6))

def greet_all(greet, first_name, *args):
    print(f"{greet}: {args}")

greet_all('Good morning', 'John', 'Brad', "Steven", "Alice")

def display_pet(type, name, color, **kwargs):
    print(kwargs)
    print(f"{name} is a {color} {type}")


pet_info = {
    "type": "cat",
    "name": "Seasame",
    "color": "black"
}

display_pet(type="cat", name="Seasame", color="black", age=25, height=1.53)
display_pet(**pet_info)

def all_args_demo(a, b, *args, c=10, **kwargs):
    print(f"a={a} b={b}") # required positional args
    print(f"args={args}") #extra optional positional args
    print(f"c={c}") # default arg
    print(f"kwargs={kwargs}") # extra keyword args
    
all_args_demo(1,2, 3, 4, 5, c=20, x=200, y=300)
all_args_demo(1,2, 3, 4, 5, x=200, y=300)
