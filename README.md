# bibliographer

"Enumerative bibliography is a procedure that identifies books in specific collection or library" (с)

# What is it and what is it for

I am quite often download huge book collections. It is really often case for file names to be like `byoll_genrih_poezd_pribyvaet_po_raspisaniyu.fb2`.

This library was a simple script for batch renaming at first. You run the script, it search for files with names encoded with translit (it is the method of encoding Cyrillic letters with Latin ones), collect the names and opens file with names. You edit the names, save and close the file and then script rename all the files listed in the file.


# Requirements
```
$ pip install -r requirements.txt
```
# Non-python requirements
`$ brew cask install sublime-text`


# To do
- [] convert script to python package
- [] Makefile, tests
- [] migrate from Fire to plumbub
- [] changelog
