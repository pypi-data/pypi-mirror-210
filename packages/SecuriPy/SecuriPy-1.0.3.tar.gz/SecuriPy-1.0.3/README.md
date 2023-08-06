# SecuriPy

SecuriPy is a Python library that provides a set of functions for encrypting and decrypting human-readable messages into undefined non-readable characters. It offers a simple yet powerful way to protect sensitive information from unauthorized access.

## Installation

To use SecuriPy, you will need Python 3.x installed on your system. You can install SecuriPy using pip, the Python package installer, by executing the following command:

```shell
pip install SecuriPy
```

## Usage

Import the `SecuriPy` module in your Python script to access the functions:

```python
from SecuriPy import encrypt, decrypt, pwd
```
OR
```python
from SecuriPy import *

### `encrypt(message, secret_key)`

The `encrypt` function takes two parameters: `message` and `secret_key`. It encrypts the provided `message` using the given `secret_key` and returns the encrypted result.

Example:
```python
message = "Hello, World!"
secret_key = "my-secret-key"

encrypted_message = encrypt(message, secret_key)
print(encrypted_message)
```

Output:
```
ե֎Չ֏քԿՂլ֓ՏևչՊԽĵŁõĻĭīĺĭļõĳĭŁĵ
```

### `decrypt(encrypted_message, password)`

The `decrypt` function takes two parameters: `encrypted_message`and `password`. It decrypts the provided `encrypted_message` using the given `secret_key` that is embeded in the `encrypted_message` and returns the original human-readable message.

Example:
```python
encrypted_message = "ե֎Չ֏քԿՂլ֓ՏևչՊԽĵŁõĻĭīĺĭļõĳĭŁĵ'"
secret_key = "my-secret-key"

decrypted_message = decrypt(encrypted_message, secret_key)
print(decrypted_message)
```

Output:
```
Hello, World!
```

### `pwd()`

The `pwd` function generates a secret password that can be used for encryption and decryption. It takes two parameters `message` and `password`. With respect to the message it generates a a secret key. It returns the secret key as a string.

## Security Considerations

- Once the encryption is done you won't be able to access the secret key.
- Use a strong and unique `secret_key` for each encryption operation to enhance security. Avoid using easily guessable or common phrases.
- Always encrypt sensitive information before storing or transmitting it. SecuriPy is a tool for obfuscating the data but does not provide additional security measures for data storage or transmission.

## Contributing

Contributions to SecuriPy are welcome! If you find any issues or have suggestions for improvement, please create a GitHub issue or submit a pull request.

## License

SecuriPy is released under the [MIT License](https://opensource.org/licenses/MIT). See the [LICENSE](https://github.com/Anupam1707/SecuriPy/blob/main/LICENSE) file for more details.

## Contact

If you have any questions, suggestions, or feedback, you can reach out to the project maintainers at [programmer.tiak@gmail.com](mailto:programmer.tiak@gmail.com).

Happy encrypting with SecuriPy!