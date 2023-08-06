

import hashlib as _hashlib
import string as _string

def Hash(text:str, hashFunc=_hashlib.sha256()) -> str:
    hashFunc.update(text.encode())
    return hashFunc.hexdigest()

def Random(length:int, charset=_string.ascii_letters + _string.digits):
    '''
    Generates random string with a specified length and consisting of specified charset
    
    :param charset: 
        * a simple string of different characters to sample the random string from.
            repeating same characters multiple times, increases probability of that character being picked more often.
        * You can enter your own characters or/and combine with defaults below.
            * string.ascii_lowercase - a-z
            * string.ascii_uppercase - A-Z
            * string.ascii_letters - lowercase + uppercase
            * string.digits - 0-9
            * string.punctuation -- all symbols
            * string.printable -- a string containing all ASCII characters considered printable
    '''
    import random

    return ''.join([random.choice(charset) for _ in range(length)])

def IndentText(text:str, indentLevel=0, indentStyle='\t'):
    ''' per indentLevel adds one indentStyle to each row '''
    from io import StringIO
    
    indentBuilder = StringIO()
    for i in range(indentLevel):
        indentBuilder.write(indentStyle)
    indentStyle = indentBuilder.getvalue()

    stringBuilder = StringIO()
    stringBuilder.write(indentStyle)
    stringBuilder.write(text.replace("\n", f"\n{indentStyle}"))

    return stringBuilder.getvalue()

def IsNullOrEmpty(text:str|None):
    if(text is None or text == ""):
        return True
    return False

def IsEqualIgnoreCase(text1:str, text2:str):
    return text1.lower() == text2.lower()

def IsEqualAnyIgnoreCase(text:str, textList:list[str]):
    lower_string = text.lower()
    lower_string_list = [s.lower() for s in textList]
    return lower_string in lower_string_list