# Arbitrary Keyword Arguments - **kwargs
# If you do not know how many keyword arguments will be passed into your function,
# add two asterisks ** before the parameter name.

# This way, the function will receive a dictionary of arguments and can access the items accordingly:

# Using **kwargs to accept any number of keyword arguments:
def my_function(**kid):
  print("His last name is " + kid["lname"])

my_function(fname = "Tobias", lname = "Refsnes")


# The **kwargs parameter allows a function to accept any number of keyword arguments.
# Inside the function, kwargs becomes a dictionary containing all the keyword arguments:

# Accessing values from **kwargs:
def my_function(**myvar):
  print("Type:", type(myvar))
  print("Name:", myvar["name"])
  print("Age:", myvar["age"])
  print("All data:", myvar)

my_function(name = "Tobias", age = 30, city = "Bergen")


# You can combine regular parameters with **kwargs.
# Regular parameters must come before **kwargs:

def my_function(username, **details):
  print("Username:", username)
  print("Additional details:")
  for key, value in details.items():
    print(" ", key + ":", value)

my_function("emil123", age = 25, city = "Oslo", hobby = "coding")


# Combining *args and **kwargs
# You can use both *args and **kwargs in the same function.

#     The order must be:
#        1 regular parameters
#        2 *args
#        3 **kwargs

def my_function(title, *args, **kwargs):
  print("Title:", title)
  print("Positional arguments:", args)
  print("Keyword arguments:", kwargs)

my_function("User Info", "Emil", "Tobias", age = 25, city = "Oslo")

# The * and ** operators can also be used when calling functions to unpack (expand) a list 
# or dictionary into separate arguments.

# Unpacking Lists with *
# If you have values stored in a list, you can use * to unpack them into individual arguments:
# Using * to unpack a list into arguments:

def my_function(a, b, c):
  return a + b + c

numbers = [1, 2, 3]
result = my_function(*numbers) # Same as: my_function(1, 2, 3)
print(result)


# Unpacking Dictionaries with **
# If you have keyword arguments stored in a dictionary, you can use ** to unpack them:

def my_function(fname, lname):
  print("Hello", fname, lname)

person = {"fname": "Emil", "lname": "Refsnes"}
my_function(**person) # Same as: my_function(fname="Emil", lname="Refsnes")


