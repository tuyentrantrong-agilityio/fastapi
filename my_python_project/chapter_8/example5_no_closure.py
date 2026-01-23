"""Apples and Bananas"""

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


# -------------------------------------------------
def replace_vowels_helper(text, vowel):
    """Replace vowels using helper function without closure.

    Args:
        text (str): Input text to transform
        vowel (str): Single character to replace vowels with

    Returns:
        str: Text with vowels replaced
    """
    return "".join(new_chart(char, vowel) for char in text)


# -------------------------------------------------
def new_chart(chart, vowel):
    """Return a given vowel if a char is a vowel else the char"""
    return vowel if chart in "aeiou" else vowel.upper() if chart in "AEIOU" else chart


# -------------------------------------------------
def main():
    """Make a jazz noise here"""
    args = get_args()
    result = replace_vowels_helper(args.text, args.vowel)
    print(result)


# -------------------------------------------------
if __name__ == "__main__":
    main()
