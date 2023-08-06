"""
This package provides a set of tools for string fragmentation.
Fragmentation in the scope of this package mean a slicing technique similar to str.split()
methode but instead using specified character as delimiter, the fragmentation in
this package use the indexes as point of slicing.

Use Case:
---------
This can be useful to search and identify miss-match string, for example string extracted
by OCR tool.

Some Terminology:
-----------------
- Fragmentation: The technique or algorithm implemented in this package to slice a string.
- Fragment: A slice of string, the smallest unit.
- Fragments: One combination of a sliced string, A unit contain a list of fragment.
"""
from core import Fragment
from rematch import REM

__version__ = '0.1.0'
