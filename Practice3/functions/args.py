# By default, a function must be called with the correct number of arguments.

# However, sometimes you may not know how many arguments that will be passed into your function.

# *args and **kwargs allow functions to accept a unknown number of arguments.




# Arbitrary Arguments - *args
        
    # If you do not know how many arguments will be passed into your function, add a * before the parameter name.
    # This way, the function will receive a tuple of arguments and can access the items accordingly:

# Using *args to accept any number of arguments:
def my_function(*kids):
  print("The youngest child is " + kids[2])

my_function("Emil", "Tobias", "Linus")


# The *args parameter allows a function to accept any number of positional arguments.
# Inside the function, args becomes a tuple containing all the passed arguments:

# Accessing individual arguments from *args:
def my_function(*args):
  print("Type:", type(args))
  print("First argument:", args[0])
  print("Second argument:", args[1])
  print("All arguments:", args)

my_function("Emil", "Tobias", "Linus")



# *args is useful when you want to create flexible functions:

# A function that calculates the sum of any number of values:

def my_function(*numbers):
  total = 0
  for num in numbers:
    total += num
  return total

print(my_function(1, 2, 3))
print(my_function(10, 20, 30, 40))
print(my_function(5))


# Finding the maximum value:
def my_function(*numbers):
  if len(numbers) == 0:
    return None
  max_num = numbers[0]
  for num in numbers:
    if num > max_num:
      max_num = num
  return max_num

print(my_function(3, 7, 2, 9, 1))



