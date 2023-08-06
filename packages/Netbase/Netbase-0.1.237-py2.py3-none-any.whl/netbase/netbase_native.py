import ctypes
import sys
from ctypes import cdll

if sys.platform=='darwin':
	lib = cdll.LoadLibrary('./netbase.dylib')
else:
	lib = cdll.LoadLibrary('./netbase.so')

print(lib._version())

