# random_names
Convert int to random name, like tree_dance and convert it back to same int.

Like [git-name](https://pypi.org/project/git-name/) which converts hashes to memorable names and back.

Also like the [Mnemonic Major System](https://en.wikipedia.org/wiki/Mnemonic_major_system) which converts
strings of numbers it phrases to aid in memorization, implemented here [mnemonic-major-encoder](https://pypi.org/project/mnemonic-major-encoder/)
In action here: https://major-system.info/en/

Usage
-----
```
from random_names.make_names import number_to_name,number_from_name

# TODO: needs a user specified separator
name = number_to_name(100,"prefix","q")
print(name) # prefix_q_activated

number = number_from_name(name)
assert number==100
```

# Why
Lets say that your users need to type in a long number, 48342342. It would be easier to
type in tree_dance. But your app still needs that number, so you need to convert it
back. This is similar to [docker container names](https://github.com/moby/moby/blob/master/pkg/namesgenerator/names-generator.go), except reversable.

# How
I map 10,000 words to 4 digits, twice. That yields two words
covering 100,000,000 numbers.

If you use a short word list, you can't generate enough names.

If you use any dictionary, you get a lot of funny, obscene or offensive names. So
I ran the world list through cuss word detection & removed most of the worst.

Docs
----
- [To do](TODO.md)


Related Pypi Packages
--
Crypocurrency related
- [mnemonic](https://pypi.org/project/mnemonic/) Words to cryptocurrency "wallet"

Mneumonic Major System
- [major_system](https://pypi.org/project/major_system/)
- [mnemonic-major-encoder](https://pypi.org/project/mnemonic-major-encoder/)

Converting arabic numbers, e.g. 22, to spoken equivalent, e.g. twenty-two and back.
- [inflect](https://pypi.org/project/inflect/) Converts, 22 to twenty-two
- [words2num](https://pypi.org/project/words2num/) Converts twenty-two to 22.
- [num2words](https://pypi.org/project/num2words/) Converts 22 to twenty-two
- [text2num](https://pypi.org/project/text2num/) Converts twenty-two to 22. Multilingual
- [num2rus](https://pypi.org/project/num2rus/) Converts 22 to Russian currency
- [num2fawords](https://pypi.org/project/num2fawords/) Convert number to Persian
- [zahlwort2num](https://pypi.org/project/zahlwort2num/) Convert german to 22.

Converting numbers to a shorter string, like [Ascii85](https://en.wikipedia.org/wiki/Ascii85)
- [num-shorty](https://pypi.org/project/num-shorty/)
- [ascii85](https://github.com/euske/pdfminer/blob/master/pdfminer/ascii85.py)

Random names, just random names. No way to convert to a number
- [pypi search](https://pypi.org/search/?q=random+name) To many to list, mostly just a function or two.
