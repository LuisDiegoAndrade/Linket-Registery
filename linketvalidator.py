#!/usr/local/bin/python3
import re

def clean_whitespace(str):
    clean = re.sub(' +', ' ', str)
    return clean

def is_allowed(str):
        match = re.search(r'^[\w\s#_:/.@]+$',str)
        try:
            match.group()
            return True
        except:
            return False


if __name__ == '__main__':

    #Try to break me here I'll give a reward ;)
    test = "#Lo"
    stripped = clean_whitespace(test)
    print(stripped)

    if is_allowed(stripped):
        print("Valid!")
    else:
        print("User Input has invalid character(s)!")
