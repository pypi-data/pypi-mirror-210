# slimpy
A simple library that provides custom string slicing and matching.

slimpy provides a convenient solution for searching and identifying strings
that may have unexpected characters. It is useful for searching and identifying 
an expected string but has mismatched characters, for example, strings 
extracted from OCR tools like pytesseract. In fact, that is the reason behind 
the creation of this library.

For example, suppose there is a script that extracts text from an image 
and there is an expected word to be present in the extracted text:

```python
expected_word = "character"
extracted_text = "This sentence has one typo word that has two mismatch oharaoter"
expected_word in extracted_text
>>> False

# We can use this library to tackle this kind of occasion
from slimpy import Fragment, REM

word_Fragment = Fragment(expected_word)
matching = REM()
matching.set_reference(extracted_text)
match = matching.perform_matching(word_Fragment)
match
>>> 
Fragmented string: character
Pattern match    : .{0,1}hara.*?ter
List of match    : ['oharaoter']

match.match
>>> oharaoter
match.pattern
>>> .{0,1}hara.*?ter
```

That's it! As mentioned earlier, searching and identifying strings that may 
have unexpected characters. 
For more information, visit the GitHub [page](https://github.com/max-efort/slimpy).
