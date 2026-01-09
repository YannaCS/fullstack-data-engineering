# Dict - Dictionary

# create dict

person = {"name": "Steven", "age": 25, "city": "beijing"}
empty = {}

# accessing value
print(person["name"])
print(person.get("age"))
# print(person["country"]) # raise error
print(person.get("country"))
print(person.get("country", "China"))

# search value
print("name" in person)

# interate
for key, value in person.items():
    print(f"{key} : {value}")

# update
person["name"] = 'John'
print(person)
person.update({"country": "China", "name": "Brad"})
print(person)

# combine
defaults = {"color": "Red", "size": "m"}
custom = {"size": "L"}

final = {**defaults, **custom}
print(final)

# dict common methods
print(person.keys())
print(person.items())
print(person.values())

# dict comprehension

evens_dict = {x: x**2 for x in range(10) if x % 2 == 0}
print(evens_dict)

prices = {"apple": 1.5, "pear": 2}
discounted_prices = {name: price * 0.9 for name, price in prices.items()}
print(discounted_prices)

# remove items from a dictionary
# 1. del — remove by key (raises error if key missing)
d = {"a": 1, "b": 2, "c": 3}
del d["b"]

print(d)  # {'a': 1, 'c': 3}

# 2. pop() — remove by key and return value (safe option)
d = {"a": 1, "b": 2, "c": 3}
value = d.pop("b")

print(value)  # 2
print(d)      # {'a': 1, 'c': 3}

d.pop("x", None)    # Safe removal (no error if key missing)

# 3. popitem() — remove last inserted key-value pair (Python 3.7+)
d = {"a": 1, "b": 2}
k, v = d.popitem()

print(k, v)  # b 2

# 4. Dictionary comprehension — remove by condition
d = {"a": 1, "b": 2, "c": 3}
d = {k: v for k, v in d.items() if k != "b"}
# Remove multiple keys
remove_keys = {"b", "c"}
d = {k: v for k, v in d.items() if k not in remove_keys}

# 5. Clear all items
d.clear()