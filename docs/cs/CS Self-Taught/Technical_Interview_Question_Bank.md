# Technical Interview Question Bank

Welcome to the Technical Interview Question Bank! This document contains detailed walkthroughs for some of the most common and important coding interview questions across various categories.

## 1. Arrays & Hashing

### Two Sum
**Problem:** Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

**Approach:**
Use a Hash Map to store the values we have seen so far and their indices. As we iterate through the array, we check if the complement (`target - current_val`) exists in our Hash Map.

**Code (Python):**
```python
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

**Complexity Analysis:**
- **Time Complexity:** $O(N)$ because we iterate through the list at most once. Hash Map lookups take $O(1)$ time on average.
- **Space Complexity:** $O(N)$ because we store at most $N$ elements in the Hash Map.

## 2. Pointers & Sliding Window

### Longest Substring Without Repeating Characters
**Problem:** Given a string `s`, find the length of the longest substring without repeating characters.

**Approach:**
Use a sliding window (two pointers) and a Set (or Hash Map) to track characters in the current window. Expand the right pointer. If a duplicate is found, shrink the left pointer until the duplicate is removed.

**Code (Python):**
```python
def lengthOfLongestSubstring(s):
    char_set = set()
    left = 0
    max_length = 0
    
    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_length = max(max_length, right - left + 1)
        
    return max_length
```

**Complexity Analysis:**
- **Time Complexity:** $O(N)$ where $N$ is the length of string `s`. Each character is visited at most twice (once by `right` and once by `left`).
- **Space Complexity:** $O(min(N, M))$ where $M$ is the size of the character set (e.g., 26 for lowercase English letters).

## 3. Linked Lists

### Reverse Linked List
**Problem:** Given the `head` of a singly linked list, reverse the list, and return the reversed list.

**Approach:**
Iterate through the list, changing the `next` pointer of the current node to point to the previous node. Keep track of `prev`, `curr`, and `next` nodes.

**Code (Python):**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverseList(head):
    prev, curr = None, head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev
```

**Complexity Analysis:**
- **Time Complexity:** $O(N)$ because we traverse the list exactly once.
- **Space Complexity:** $O(1)$ as we only use a few pointers.

## 4. Trees & Graphs

### Number of Islands
**Problem:** Given an `m x n` 2D binary grid `grid` which represents a map of '1's (land) and '0's (water), return the number of islands.

**Approach:**
Iterate through every cell. When a '1' is found, increment the island count, and launch a DFS/BFS to mark all connected '1's as visited (e.g., by changing them to '0' or storing in a visited set).

**Code (Python):**
```python
def numIslands(grid):
    if not grid: return 0
    
    def dfs(r, c):
        if r < 0 or c < 0 or r >= len(grid) or c >= len(grid[0]) or grid[r][c] == '0':
            return
        grid[r][c] = '0' # mark as visited
        dfs(r-1, c)
        dfs(r+1, c)
        dfs(r, c-1)
        dfs(r, c+1)
        
    islands = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == '1':
                islands += 1
                dfs(r, c)
    return islands
```

**Complexity Analysis:**
- **Time Complexity:** $O(M \times N)$ where $M$ is the number of rows and $N$ is the number of columns.
- **Space Complexity:** $O(M \times N)$ in the worst case for the DFS recursion stack.

## 5. Dynamic Programming

### Climbing Stairs
**Problem:** You are climbing a staircase. It takes `n` steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?

**Approach:**
This is fundamentally the Fibonacci sequence. The ways to reach step `i` is the sum of ways to reach `i-1` and `i-2`. We can optimize the space to $O(1)$ by just keeping track of the last two values.

**Code (Python):**
```python
def climbStairs(n):
    if n <= 2: return n
    one, two = 1, 2
    for i in range(3, n + 1):
        temp = one + two
        one = two
        two = temp
    return two
```

**Complexity Analysis:**
- **Time Complexity:** $O(N)$ to compute the sequence up to $n$.
- **Space Complexity:** $O(1)$ as we only maintain two variables.
