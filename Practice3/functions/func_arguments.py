# Information can be passed into functions as arguments.

# Arguments are specified after the function name, inside the parentheses.
# You can add as many arguments as you want, just separate them with a comma.

# The following example has a function with one argument (fname).
#  When the function is called, we pass along a first name, which is used inside the function to print the full name:




# A function with one argument:
def my_function(fname):
  print(fname + " Refsnes")

my_function("Emil")
my_function("Tobias")
my_function("Linus")


# From a function's perspective:

    # A parameter is the variable listed inside the parentheses in the function definition.

    # An argument is the actual value that is sent to the function when it is called.


def my_function(name): # name is a parameter
  print("Hello", name)

my_function("Emil") # "Emil" is an argument



# Number of Arguments
    # If your function expects 2 arguments, you must call it with exactly 2 arguments.

def my_function(fname, lname):
  print(fname + " " + lname)

my_function("Emil", "Refsnes")




#You can assign default values to parameters.
# If the function is called without an argument, it uses the default value:

def my_function(name = "friend"):
  print("Hello", name)

my_function("Emil")
my_function("Tobias")
my_function()
my_function("Linus")
