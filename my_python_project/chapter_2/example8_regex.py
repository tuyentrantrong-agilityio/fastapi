"""Apples and Bananas"""

import argparse
import os
import re


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

    # new_text = re.sub(
    #     "[aeiou]",
    #     vowel,
    #     args.text,
    # )
    # new_text = re.sub("[AEIOU]", vowel.upper(), new_text)
    new_text = re.sub(
        "[aeiouAEIOU]",
        lambda x: vowel.upper() if x.group().isupper() else vowel,
        args.text,
    )
    # Need to use . group() because re.sub passes a Match object to the lambda, not the character itself
    print(new_text)


# -------------------------------------------------


def new_chart(chart, vowel):
    return vowel if chart in "aeiou" else vowel.upper() if chart in "AEIOU" else chart


# -------------------------------------------------
if __name__ == "__main__":
    main()
