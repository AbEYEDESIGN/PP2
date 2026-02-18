# Lambda functions are commonly used with built-in functions like map(), filter(), and sorted().

# Using Lambda with map()

    # The map() function applies a function to every item in an iterable:    
# Double all numbers in a list:
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)


# Using Lambda with filter()
    # The filter() function creates a list of items for which a function returns True:
# Filter out even numbers from a list:
numbers = [1, 2, 3, 4, 5, 6, 7, 8]
odd_numbers = list(filter(lambda x: x % 2 != 0, numbers))
print(odd_numbers)

# Using Lambda with sorted()
    # The sorted() function can use a lambda as a key for custom sorting:
# Sort a list of tuples by the second element:
students = [("Emil", 25), ("Tobias", 22), ("Linus", 28)]
sorted_students = sorted(students, key=lambda x: x[1])
print(sorted_students)

# Sort strings by length:
words = ["apple", "pie", "banana", "cherry"]
sorted_words = sorted(words, key=lambda x: len(x))
print(sorted_words)


# Exercise
# What will be the result of the following code:
x = lambda a, b : a - b
print(x(5, 3))

#answer: 2
