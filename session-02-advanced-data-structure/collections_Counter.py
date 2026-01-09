# import
from collections import Counter

"""create a counter"""
# 1. From a string
c = Counter("hello")  # Counter({'l': 2, 'h': 1, 'e': 1, 'o': 1})

# 2. From a list
c = Counter([1, 2, 2, 3, 3, 3])  # Counter({3: 3, 2: 2, 1: 1})

# 3. From a dictionary
c = Counter({'a': 3, 'b': 2})  # Counter({'a': 3, 'b': 2})

# 4. Empty counter
c = Counter()


"""access elements"""
c = Counter("hello")

# Get count (returns 0 if key doesn't exist, no KeyError!)
c['l']  # 2
c['z']  # 0 (not KeyError)

# Check if key exists
'h' in c  # True
'z' in c  # False

# Get all keys
list(c.keys())  # ['h', 'e', 'l', 'o']

# Get all values (counts)
list(c.values())  # [1, 1, 2, 1]

# Get items
list(c.items())  # [('h', 1), ('e', 1), ('l', 2), ('o', 1)]


""" modify counter"""
c = Counter("hello")

# Add counts
c['l'] += 1  # Counter({'l': 3, 'h': 1, 'e': 1, 'o': 1})

# Subtract counts
c['l'] -= 1  # Counter({'l': 1, 'h': 1, 'e': 1, 'o': 1})

# Set count
c['z'] = 5

# Delete element
del c['h']

# Update (add counts from another iterable/Counter)
c.update("world")  # Adds counts
c.update({'a': 3})

# Subtract (subtract counts)
c.subtract("lo")  # Subtracts counts


"""common methods"""
c = Counter("hello world")

# most_common(n) - returns n most common elements as list of tuples
c.most_common()     # All elements, sorted by count (descending)
c.most_common(3)    # Top 3 most common

# elements() - returns iterator with elements repeated by their counts
list(c.elements())  # ['h', 'e', 'l', 'l', 'l', 'o', ...]

# total() - sum of all counts (Python 3.10+)
c.total()  # 11

# clear() - remove all elements
c.clear()


"""arithmetic operations"""
c1 = Counter(['a', 'b', 'b', 'c'])
c2 = Counter(['b', 'c', 'c', 'd'])

# Addition (add counts)
c1 + c2  # Counter({'b': 3, 'c': 3, 'a': 1, 'd': 1})

# Subtraction (subtract counts, keep only positive)
c1 - c2  # Counter({'a': 1, 'b': 1})

# Intersection (minimum counts)
c1 & c2  # Counter({'b': 1, 'c': 1})

# Union (maximum counts)
c1 | c2  # Counter({'b': 2, 'c': 2, 'a': 1, 'd': 1})

# Unary operations
+c1  # Remove zero and negative counts
-c1  # Negate counts, remove positive/zero



"""comparison"""
c1 = Counter("abc")
c2 = Counter("abc")
c3 = Counter("def")

# Equality
c1 == c2  # True
c1 == c3  # False

# Note: Missing elements are treated as having count 0
Counter({'a': 1}) == Counter({'a': 1, 'b': 0})  # True


"""Common Patterns for LeetCode"""
# Pattern 1: Count frequency
# Count character frequency
s = 'string'
counter = Counter(s)

# Count with condition
arr = [1, 2, 3, 3, -1]
counter = Counter(x for x in arr if x > 0)

# Pattern 2: Check if two strings are anagrams
s1 = 'string'
s2 = 'stingr'
Counter(s1) == Counter(s2)

# Pattern 3: Find missing/extra elements
list1 = ['a', 'b', 'b', 'c']
list2 = ['b', 'c', 'c', 'd']
c1 = Counter(list1)
c2 = Counter(list2)

missing = c1 - c2  # Elements in list1 but not enough in list2
extra = c2 - c1    # Elements in list2 but not enough in list1


# Pattern 4: Sliding window with Counter
pattern = 'abc'
s = "cbaebabacd"
need = Counter(pattern)
window = Counter(s[:len(pattern)])

# Slide
for i in range(len(pattern), len(s)):
    window[s[i]] += 1
    
    left = i - len(pattern)
    window[s[left]] -= 1
    if window[s[left]] == 0:
        del window[s[left]]  # Clean up zeros
    
    if window == need:
        # Found match
        pass

# Pattern 5: Find top k frequent elements
nums = [3, 3, 2, 1, 4, 5]
k = 2
counter = Counter(nums)
print([num for num, _ in counter.most_common(k)])

# Pattern 6: Check if enough resources
inventory = {'book1': 3, 'book2': 2}
order = {'book1': 1, 'book2': 3}
available = Counter(inventory)
needed = Counter(order)

# Can fulfill order if available >= needed for each item
# needed - abailable: in needed not in available
can_fulfill = not (needed - available)  # Empty counter means yes

"""
Tips

- Counter always returns 0 for missing keys (unlike dict which raises KeyError)
- Arithmetic operations keep only positive counts (except subtraction with - unary)
- Use del or set to 0 to remove elements (they're equivalent for comparison)
- Counter is a subclass of dict, so all dict methods work
- For sliding window: manually delete zero-count elements to avoid memory issues

Time Complexity

- Counter(iterable): O(n)
- most_common(): O(n log n)
- most_common(k): O(n log k)
- +, -, &, |: O(len(c1) + len(c2))
- Comparison ==: O(min(len(c1), len(c2)))
"""