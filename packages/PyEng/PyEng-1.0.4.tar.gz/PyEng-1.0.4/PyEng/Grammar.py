# PyEng - Grammar

''' This is the "Grammar" module. '''

# Function 1 - Capitalized
def capitalized(phrase):
    if (isinstance(phrase, str)):
        # Variables
        firstChar = phrase[0]

        # Checking if Phrase is Capitalized
        if (firstChar >= "A" and firstChar <= "Z"):
            return True
        elif (firstChar >= "a" and firstChar <= "z"):
            return False
    else:
        raise Exception("The 'phrase' argument must be a string.")