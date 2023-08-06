"""Encrypter and Decrypter of Readable Messages Using Python by Anupam Kanoongo"""

def pwd(message, key):
    """Generates a non-readable key to encrypt the text"""
    key = list(key) 
    for i in range(len(key)):
        x = (ord(key[i]) + 200)
        key[i] = chr(x)
        
    if len(message) == len(key):
        return(key) 
    elif len(message) > len(key):
        for i in range(len(message) -len(key)):
            key.append(key[i % len(key)])
        return("" . join(key)) 
    elif len(message) < len(key):
        key = key[:len(message)]
        return("" . join(key))
    
def encrypt(message,password):
    """Encrypts the given text with respect to the key generated and embeds the key in the encrypted text"""
    message = message + " "
    key = pwd(message, password)
    encrypted_text = []
    for i in range(len(message)):
        x = (ord(message[i]) +ord(key[i]) + 1000)
        encrypted_text.append(chr(x))
    encrypted_text = ("" . join(encrypted_text))
    key = ("".join(key))
    return encrypted_text+key , key

def decrypt(encrypted_text, password):
    """Figures out the key from the encrypted text and decryptes it with respect to the key"""
    orig_text = []
    b = int(len(encrypted_text)/2)
    key = encrypted_text[b:]
    encrypted_text = encrypted_text[:b-1]
    if key == password:
        for i in range(len(encrypted_text)):
            x = (ord(encrypted_text[i]) -ord(key[i]) - 1000)
            orig_text.append(chr(x))
        orig_text = ("" . join(orig_text))
        return orig_text
    else:
        return "Message is corrupt or Password is incorrect"
