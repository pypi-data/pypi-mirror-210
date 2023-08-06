# PyComputer - Volume

''' This is the "Volume" module. '''

# Imports
import os

# The Directory
directory = os.path.dirname(os.path.realpath(__file__)).replace(os.sep, "/")

# Function 1 - Max
def max():
    os.chdir(directory + "/assets")

    os.system("setvol 100")

# Function 2 - Min
def min():
    os.chdir(directory + "/assets")

    os.system("setvol 0")

# Function 3 - Increase
def increase(value):
    if (isinstance(value, int)):
        os.chdir(directory + "/assets")

        os.system("setvol +" + str(value))
    else:
        raise Exception("The 'value' argument must be an integer.")

# Function 4 - Decrease
def decrease(value):
    if (isinstance(value, int)):
        os.chdir(directory + "/assets")

        os.system("setvol -" + str(value))
    else:
        raise Exception("The 'value' argument must be an integer.")

# Function 5 - Mute
def mute():
    os.chdir(directory + "/assets")

    os.system("setvol mute")

# Function 6 - Unmute
def unmute():
    os.chdir(directory + "/assets")

    os.system("setvol unmute")

# Function 7 - Set
def set(value):
    if (isinstance(value, int)):
        os.chdir(directory + "/assets")

        os.system("setvol " + str(value))
    else:
        raise Exception("The 'value' argument must be an integer.")