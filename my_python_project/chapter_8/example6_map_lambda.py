"""Apples and Bananas"""

import argparse
import os
from functools import partial


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
def replace_vowels_map_lambda(text, vowel):
    """Replace vowels using map() with lambda function.

    Args:
        text (str): Input text to transform
        vowel (str): Single character to replace vowels with

    Returns:
        str: Text with vowels replaced
    """
    return "".join(
        map(
            lambda char: vowel
            if char in "aeiou"
            else vowel.upper()
            if char in "AEIOU"
            else char,
            text,
        )
    )


# -------------------------------------------------
def main():
    """Make a jazz noise here"""
    args = get_args()
    result = replace_vowels_map_lambda(args.text, args.vowel)
    print(result)


# -------------------------------------------------
def new_chart(chart, vowel):
    return vowel if chart in "aeiou" else vowel.upper() if chart in "AEIOU" else chart


# -------------------------------------------------
if __name__ == "__main__":
    main()
