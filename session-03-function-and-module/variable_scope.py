# scope

# LEGB -> Local -> Enclosing -> Global -> Built-in

x = 'Global'

# Look up order:
# Local -> Enclosing -> global -> built in
def outer():
    x = 'x in outer'
    
    def inner():
        x = 'x in inner' # local scope 
        print(x)
        
    inner()
    print(x)
    
outer()


# closure ->  a function that returns another inner function. The returned function can access different scopes
# can be used for function factory

total_count = 0
# count = 0
def make_counter():
    count = 0

    def wrapper(): 
        count = 0
        def counter():
            # count = 0
            nonlocal count # modify the variable scope to enclosing
            global total_count
            # count += 1
            count = count + 1
            total_count += 1
            return f"count: {count}, total_count: {total_count}"    
        
        return counter

    return wrapper()

counter_1 = make_counter()
counter_2 = make_counter()

print(counter_1())
print(counter_1())
print(counter_1())

print(counter_2())
print(counter_2())


# Recursive / Recusion
# basic example - Fibonacci Sequence

# 0, 1, 1, 2, 3, 5

def fibonacci(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(3))

# fib(2) + fib(1)
# # ->
# fib(1) + fib(1)