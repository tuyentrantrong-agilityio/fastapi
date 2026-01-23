"""Apples and Bananas - Using str.replace() method"""

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


def replace_vowels_str_method(text, vowel):
    """Replace vowels using str.replace() method.

    Args:
        text: Input text string
        vowel: Replacement vowel (lowercase)

    Returns:
        Text with vowels replaced
    """
    result = text
    for char in "aeiou":
        result = result.replace(char, vowel).replace(char.upper(), vowel.upper())
    return result


def main():
    """Make a jazz noise here"""
    args = get_args()
    result = replace_vowels_str_method(args.text, args.vowel)
    print(result)


# -------------------------------------------------
if __name__ == "__main__":
    main()
