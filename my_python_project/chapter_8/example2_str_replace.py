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
def main():
    """Make a jazz noise here"""
    args = get_args()
    text = args.text
    vowel = args.vowel

    for char in "aeiou":
        text = text.replace(char, vowel).replace(char.upper(), vowel.upper())
    print(text)


# -------------------------------------------------
if __name__ == "__main__":
    main()
