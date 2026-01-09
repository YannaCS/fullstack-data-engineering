from collections import deque

# ============================================================================
# CREATION
# ============================================================================

d = deque()                      # Empty deque
d = deque([1, 2, 3])            # From iterable
d = deque('abc')                # From string → deque(['a', 'b', 'c'])
d = deque([1, 2, 3], maxlen=5)  # Fixed-size deque (auto-removes oldest)


# ============================================================================
# ADDING ELEMENTS
# ============================================================================
x=2
d.append(x)            # Add to right end - O(1)
d.appendleft(x)        # Add to left end - O(1)
d.extend([1, 2, 3])    # Extend right with iterable - O(k)
d.extendleft([1, 2, 3])  # Extend left (items added in REVERSE order) - O(k)

# Example:
d = deque([2, 3])
d.extendleft([0, 1])   # Result: deque([1, 0, 2, 3])


# ============================================================================
# REMOVING ELEMENTS
# ============================================================================

d.pop()                # Remove and return from right - O(1)
d.popleft()           # Remove and return from left - O(1)
d.remove(x)           # Remove first occurrence of x - O(n)
d.clear()             # Remove all elements


# ============================================================================
# ACCESSING ELEMENTS
# ============================================================================

d[0]                  # Access by index (supports negative indexing)
d[-1]                 # Last element
# WARNING: Random access is O(n), not O(1) like lists!


# ============================================================================
# ROTATION
# ============================================================================

d.rotate(n)           # Rotate n steps to right (negative = left)
d.rotate(1)           # Move last element to front
d.rotate(-1)          # Move first element to back

# Example:
d = deque([1, 2, 3, 4, 5])
d.rotate(2)           # Result: deque([4, 5, 1, 2, 3])
d.rotate(-1)          # Result: deque([5, 1, 2, 3, 4])


# ============================================================================
# OTHER OPERATIONS
# ============================================================================

d.count(x)            # Count occurrences of x
d.reverse()           # Reverse in-place
d.copy()              # Shallow copy (Python 3.5+)
len(d)                # Get length
x in d                # Check membership - O(n)
d.maxlen              # Max size (None if unbounded)


# ============================================================================
# COMMON PATTERNS
# ============================================================================

# Pattern 1: Queue (FIFO)
# -----------------------
q = deque()
q.append(x)           # Enqueue
x = q.popleft()       # Dequeue


# Pattern 2: Stack (LIFO)
# -----------------------
s = deque()
s.append(x)           # Push
x = s.pop()           # Pop


# Pattern 3: Sliding Window
# -------------------------
k=3
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
window = deque(maxlen=k)  # Auto-drops oldest when full
for item in data:
    window.append(item)
    # Process window of last k items


# Pattern 4: Circular Buffer
# --------------------------
buf = deque(maxlen=5)
buf.extend([1, 2, 3, 4, 5])
buf.append(6)         # Automatically removes 1, now [2, 3, 4, 5, 6]


# Pattern 5: BFS in Graph/Tree
# ----------------------------
def bfs(start_node):
    queue = deque([start_node])
    visited = set([start_node])
    
    while queue:
        node = queue.popleft()
        # Process node
        
        for neighbor in node.neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)


# Pattern 6: Monotonic Deque (for sliding window maximum/minimum)
# ---------------------------------------------------------------
def sliding_window_max(nums, k):
    dq = deque()  # Store indices
    result = []
    
    for i, num in enumerate(nums):
        # Remove elements outside window
        while dq and dq[0] <= i - k:
            dq.popleft()
        
        # Remove smaller elements (maintain decreasing order)
        while dq and nums[dq[-1]] < num:
            dq.pop()
        
        dq.append(i)
        
        if i >= k - 1:
            result.append(nums[dq[0]])
    
    return result


# ============================================================================
# TIME COMPLEXITIES
# ============================================================================

"""
Operation           Time Complexity
-----------------------------------------
append()            O(1)
appendleft()        O(1)
pop()               O(1)
popleft()           O(1)
extend()            O(k) - k is length of iterable
extendleft()        O(k)
remove()            O(n)
count()             O(n)
index()             O(n)
in (membership)     O(n)
rotate()            O(k) - k is number of steps
d[i] (indexing)     O(n) - not O(1) like lists!
reverse()           O(n)
copy()              O(n)
"""


# ============================================================================
# KEY DIFFERENCES FROM LIST
# ============================================================================

"""
Deque vs List:
--------------
1. Thread-safe append/pop from both ends
2. Memory efficient for queue operations
3. No efficient random access (lists: O(1), deque: O(n))
4. Fixed-size option with maxlen parameter
5. Deque doesn't have sort() method
6. List is faster for random access and iteration

Use deque when:
- You need fast append/pop from both ends
- Implementing queues, stacks, or sliding windows
- Need bounded/circular buffer (maxlen)

Use list when:
- You need fast random access
- You need to sort in-place
- You mostly work with middle elements
"""


# ============================================================================
# PRACTICAL EXAMPLES
# ============================================================================

# Example 1: Recent N items tracker
recent_items = deque(maxlen=10)  # Only keeps last 10 items
for item in stream:
    recent_items.append(item)


# Example 2: Palindrome checker
def is_palindrome(s):
    d = deque(s.lower())
    while len(d) > 1:
        if d.popleft() != d.pop():
            return False
    return True


# Example 3: Undo/Redo functionality
undo_stack = deque(maxlen=50)    # Last 50 actions
redo_stack = deque(maxlen=50)

def perform_action(action):
    undo_stack.append(action)
    redo_stack.clear()

def undo():
    if undo_stack:
        action = undo_stack.pop()
        redo_stack.append(action)
        # Revert action

def redo():
    if redo_stack:
        action = redo_stack.pop()
        undo_stack.append(action)
        # Reapply action


# Example 4: Moving average
class MovingAverage:
    def __init__(self, size):
        self.queue = deque(maxlen=size)
        self.sum = 0
    
    def next(self, val):
        if len(self.queue) == self.queue.maxlen:
            self.sum -= self.queue[0]
        self.queue.append(val)
        self.sum += val
        return self.sum / len(self.queue)


# Example 5: Task scheduler with priorities
from collections import deque

high_priority = deque()
low_priority = deque()

def add_task(task, priority='low'):
    if priority == 'high':
        high_priority.append(task)
    else:
        low_priority.append(task)

def get_next_task():
    if high_priority:
        return high_priority.popleft()
    elif low_priority:
        return low_priority.popleft()
    return None