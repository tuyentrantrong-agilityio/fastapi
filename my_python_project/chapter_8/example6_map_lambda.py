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
def main():
    """Make a jazz noise here"""
    args = get_args()
    vowel = args.vowel

    # Method 1: Use partial to create a new function with keyword-only arguments
    # This approach binds the vowel argument to the new_chart function
    # new_text = map(partial(new_chart, vowel=vowel), args.text)

    # Method 2: Use lambda to call the existing function with captured vowel variable
    # This approach wraps the function call in a lambda expression
    # new_text = map(lambda chart: new_chart(chart, vowel), args.text)

    # Method 3: Use lambda with inline conditional logic
    # This approach directly implements the logic without calling a separate function
    new_text = map(
        lambda chart: vowel
        if chart in "aeiou"
        else chart.upper()
        if chart in "AEIOU"
        else chart,
        args.text,
    )
    print("".join(new_text))


# -------------------------------------------------


def new_chart(chart, vowel):
    return vowel if chart in "aeiou" else vowel.upper() if chart in "AEIOU" else chart


# -------------------------------------------------
if __name__ == "__main__":
    main()
