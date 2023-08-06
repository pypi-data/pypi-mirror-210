from typing import Optional
from string import ascii_lowercase, ascii_letters

VOWELS_LOWERCASE = 'aeiou'
CONSONANTS_LOWERCASE = ''.join(
    [letter for letter in ascii_lowercase if letter not in VOWELS_LOWERCASE]
)
ACUTE_VOWELS_LOWERCASE = 'áéíóú'
UMLAUT_VOWELS_LOWERCASE = 'äëïöü'

ENCIRCLED = 'ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ'

GROUPS_TO_TRANSFORM = []
GROUPS_TO_TRANSFORM.append(VOWELS_LOWERCASE)
GROUPS_TO_TRANSFORM.append(CONSONANTS_LOWERCASE)
GROUPS_TO_TRANSFORM.append(ACUTE_VOWELS_LOWERCASE)
GROUPS_TO_TRANSFORM.append(UMLAUT_VOWELS_LOWERCASE)

# Add uppercase letters
for group in GROUPS_TO_TRANSFORM.copy():
    GROUPS_TO_TRANSFORM.append(group.upper())


def wrapping_slice(string: str, start: Optional[int] = 1) -> str:
    """
    Given a :string return another string beginning at :start:
        wrapping around the length of the :string:.

    Visualize this:
        Glue the beginning and the end of the given :string: and go to
        position given by :start: to make a cut there to get a list again.
    """
    index = start % len(string)
    return string[index:] + string[:index]


def find_new_text(text: str, iteration: Optional[int] = 1, encircle: Optional[str]='n') -> str:
    """
    Returns the new text that will substitute every consonant or vowel
    from the ASCII characters with the next iteration-th consonant or vowel.
    """
    for value in GROUPS_TO_TRANSFORM:
        code = (f"table = ''.maketrans('{value}', "
                f"wrapping_slice('{value}',{iteration}))")
        exec(code, globals())
        text = text.translate(table)

    if encircle == 'y':
        text = encircle_text(text)

    return text


def encircle_text(text: str) -> str:
    """
    Encircle text
    """
    text = text.upper()
    table = ''.maketrans(ACUTE_VOWELS_LOWERCASE.upper(),
                         VOWELS_LOWERCASE.upper())
    text = text.translate(table)

    table = ''.maketrans(UMLAUT_VOWELS_LOWERCASE.upper(),
                         VOWELS_LOWERCASE.upper())
    text = text.translate(table)

    table = ''.maketrans(ascii_lowercase.upper(), ENCIRCLED)
    text = text.translate(table)

    return text


def atbash(text: str) -> str:
    """
    Atbash for ascii letters only
    https://en.wikipedia.org/wiki/Atbash
    """
    atbash_letters = ascii_letters[:len(ascii_letters)//2][::-1] + ascii_letters[len(ascii_letters)//2:][::-1]
    table = ''.maketrans(ascii_letters,
                         atbash_letters)
    text = text.translate(table)

    return text


if __name__ == "__main__":
    for i in range(len(VOWELS_LOWERCASE)*len(CONSONANTS_LOWERCASE)+1):
        print(find_new_text('Taisir Avilés', i))
