# PyComputer - Brightness

''' This is the "Brightness" module. '''

# Imports
import screen_brightness_control as sbc

# Function 1 - Max
def max():
    sbc.set_brightness(100)

# Function 2 - Min
def min():
    sbc.set_brightness(0)

# Function 3 - Set
def set(value):
    if (isinstance(value, (int, float))):
        sbc.set_brightness(value)
    else:
        raise Exception("The 'value' argument must be an integer or a float.")