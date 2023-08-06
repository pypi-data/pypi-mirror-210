# PyEng - Words

''' This is the "Words" module. '''

# Imports
import os
import json
from difflib import get_close_matches

# The Directory
directory = os.path.dirname(os.path.realpath(__file__)).replace(os.sep, "/")

# Variables
dictionaryJSON = json.load(open(directory + "/data/dictionary.json", encoding="utf8"))

# Function 1 - Meaning
def meaning(word):
    # Checking the Data Type
    if (isinstance(word, str)):
        # Converting to Lower Case
        word = word.lower()

        # Checking for Meaning
        if (word in dictionaryJSON):
            return dictionaryJSON[word]
        elif (len(get_close_matches(word, dictionaryJSON.keys())) > 0):
            return "Did you mean '{0}' instead? Try it again with the correct word.".format(get_close_matches(word, dictionaryJSON.keys())[0])
        else:
            return "The word doesn't exist. Please try again."
    else:
        raise Exception("The 'word' argument must be a string.")

# Function 2 - Anagram
def anagram(phrase1, phrase2):
    # Checking the Data Type
    if (isinstance(phrase1, str) and isinstance(phrase2, str)):
        # Converting to Lower Case
        phrase1 = phrase1.lower()
        phrase2 = phrase2.lower()

        # Checking if Anagram
        return ((len(phrase1) == len(phrase2)) and (sorted(phrase1) == sorted(phrase2)))
    else:
        raise Exception("The 'phrase1' and 'phrase2' arguments must be a string.")