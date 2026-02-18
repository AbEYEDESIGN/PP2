# In Python, a function is defined using the def keyword, followed by a function name and parentheses:

def my_function():
  print("Hello from a function")

# This creates a function named my_function that prints "Hello from a function" when called.
# The code inside the function must be indented. Python uses indentation to define code blocks.



# To call a function, write its name followed by parentheses:

def my_function():
  print("Hello from a function")

my_function()

# Function names follow the same rules as variable names in Python:

    # A function name must start with a letter or underscore
    # A function name can only contain letters, numbers, and underscores
    # Function names are case-sensitive (myFunction and myfunction are different)





# Why Use Functions?
# Imagine you need to convert temperatures from Fahrenheit 
# to Celsius several times in your program. Without functions,
# you would have to write the same calculation code repeatedly:



# Without functions - repetitive code:
temp1 = 77
celsius1 = (temp1 - 32) * 5 / 9
print(celsius1)

temp2 = 95
celsius2 = (temp2 - 32) * 5 / 9
print(celsius2)

temp3 = 50
celsius3 = (temp3 - 32) * 5 / 9
print(celsius3)




# With functions, you write the code once and reuse it:
def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9

print(fahrenheit_to_celsius(77))
print(fahrenheit_to_celsius(95))
print(fahrenheit_to_celsius(50))


# A function that returns a value:
def get_greeting():
  return "Hello from a function"

message = get_greeting()
print(message)


# Using the return value directly:
def get_greeting():
  return "Hello from a function"

print(get_greeting())





# Function definitions cannot be empty. If you need to create a function placeholder without any code, use the pass statement:
# Example
def my_function():
  pass






