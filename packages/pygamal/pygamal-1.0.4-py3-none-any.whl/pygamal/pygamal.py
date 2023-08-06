""" # pygamal module in python

This module is wrapper a for ElGamal_c C extension module
it has the following function:

is_prime:
    Prime checker in c. Takes integer, returns bool.

gen_keys:
    Generate the global g, e keys from the secret key and p
     
gen_keys_FAST:
    Generate the global g, e keys from the secret key and p
    Faster

gen_c1:
    generate cypher msg 1

gen_x_key:
    generate x_key used for decrypting

encrypt:
    encrypt msg. uses p, g, e, and secret, with msg as input

decrypt:
    decrypt msg, uses p, secret, and 2 cipher msg as input

Example useage:

```python
## Define global vars ##
x = 54 # My private key

p_glob = 43051 # Global
g_glob, e_glob = gen_keys(p_glob, x)

## Define me ##
Alice = ElGamalEncryptor(p_glob, x, g_glob, e_glob)

## Define Bob ##
y = 43 # Bob private key
Bob = ElGamalEncryptor(p_glob, y, g_glob, e_glob)

####### Bob want to send message to me #######
msg = 'Hi Alice!'
c1, c2 = Bob.encrypt(msg)
print("Plain message:", msg)
print("Encrypted message:",c1, c2)

####### Bob sent me (c1, c2) #######
msg_decrypted = Alice.decrypt(c1, c2)
print("Decrypted message:", msg_decrypted)

```
"""

import ElGamal_c

class ElGamalEncryptor:
    """
    A class used to represent a Person to use Taher Elgamal

    More info: https://en.wikipedia.org/wiki/ElGamal_encryption

    

    Attributes
    ----------
    p_GLOBAL : int
        The global prime to be used for encryption

    g_GLOBAL : int
        The global g to be used for encryption

    e_GLOBAL : int
        The global e to be used for encryption

    secret : int
        The secret key for this person

    Methods
    -------
    encrypt(msg : str) -> (c1 : int, c2 : list[int])
        This method takes the message, encrypt it using the secret key and global
        keys, then return encrypted message

    decrypt(c1 : int, c2 : list[int]) -> msg : str
        This method decrypt the cipher message using secret and global keys
        then return str msg
    """

    p_GLOBAL = 0
    g_GLOBAL = 0
    e_GLOBAL = 0
    secret = 0

    def __init__(self, p, x, g, e):
        """
        Create new instance of the encryption
        takes p and secret key
        """
        self.p_GLOBAL = p
        self.secret = x

        self.g_GLOBAL, self.e_GLOBAL = g, e

    def encrypt(self, msg):
        """
        encrypt msg using private key
        return c1, c2
        """
        
        c1 = gen_c1(self.g_GLOBAL, self.secret, self.p_GLOBAL)

        c2 = encrypt(msg, self.secret, self.e_GLOBAL, self.p_GLOBAL)
        return c1, c2
    
    def decrypt(self, c1, c2):
        """
        decrypt msg using c1, c2
        return msg
        """
        x_key = gen_x_key(c1, self.secret, self.p_GLOBAL)

        msg = decrypt(c2, x_key, self.p_GLOBAL)
        return msg
    

def is_prime(number: int) -> bool:
    """
    Checks if `number` is prime or not, using C backend
    """
    return ElGamal_c.is_prime(number)

def gen_keys(p:int, x:int):
    """
    Generate the global g, e keys from the secret key and p
    """
    g, e = ElGamal_c.gen_keys(p, x)
    return g, e

def gen_keys_FAST(p:int, secret:int):
    """
    Generate the global g, e keys from the secret key and p
    Uses faster algorithm to find primitive roots
    """
    g, e = ElGamal_c.gen_keys_FAST(p, secret)
    return g, e

def gen_c1(g, secret, p) -> int:
    """
    Generate the first cipher message from g, secret and p
    """
    return ElGamal_c.gen_c1(g, secret, p)

def gen_x_key(c1, secret, p) -> int:
    """
    Generate x_key to be used to decrypt messages
    """
    return ElGamal_c.gen_x_key(c1, secret, p)

def encrypt(msg: str, secret: int, e:int, p:int) -> list[int]:
    """
    Should be used inside ElGamalEncryptor class only
    Encrypts message using keys.
    """
    return ElGamal_c.encrypt(msg+" ", secret, e, p) # added + " " because C soruce has bug

def decrypt(c2:list[int], x_key:int, p:int) -> str:
    """
    Should be used inside ElGamalEncryptor class only
    decrypts cipher message 1 and 2 using keys.
    """
    return ElGamal_c.decrypt(len(c2), *c2, x_key, p)
