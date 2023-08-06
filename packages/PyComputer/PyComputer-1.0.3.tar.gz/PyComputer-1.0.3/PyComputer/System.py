# PyComputer - System

''' This is the "System" module. '''

# Imports
import os
import platform
import wmi

# Variables
os = platform.uname().system
os_release = platform.uname().system
os_version = platform.uname().system
pc_name = platform.uname().node
machine = platform.uname().machine
processor = platform.uname().processor

manufacturer = wmi.WMI().Win32_ComputerSystem()[0].Manufacturer
model = wmi.WMI().Win32_ComputerSystem()[0].Model