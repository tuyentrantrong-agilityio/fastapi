"""Apples and Bananas - Using for loop to iterate through characters"""

import argparse
import os


def get_args():
    """get command-line argurments"""

    parser = argparse.ArgumentParser(description="Say hello")
    parser.add_argument(
        "text", metavar="text", default="World", help="Input text or file"
    )
    parser.add_argument(
        "-v",
        "--vowel",
        type=str,
        help="the vowel to substitle",
        default="a",
        choices=list("aeiou"),
    )
    args = parser.parse_args()
    if os.path.isfile(args.text):
        args.text = open(args.text).read().rstrip()

    return args


def replace_vowels_iterate(text, vowel):
    """Replace vowels by iterating through characters.

    Args:
        text: Input text string
        vowel: Replacement vowel (lowercase)

    Returns:
        Text with vowels replaced
    """
    new_text = []

    for char in text:
        if char in "aeiou":
            new_text.append(vowel)
        elif char in "AEIOU":
            new_text.append(vowel.upper())
        else:
            new_text.append(char)

    return "".join(new_text)


def main():
    """Make a jazz noise here"""
    args = get_args()
    result = replace_vowels_iterate(args.text, args.vowel)
    print(result)


# -------------------------------------------------
if __name__ == "__main__":
    main()
