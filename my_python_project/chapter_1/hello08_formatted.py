#!/usr/bin/env python3
"""
Docstring for my_python_project.chapter_1.hello08_formatted


"""

import argparse


# ----------------------------
def get_args():
    """Get the command line agruments"""
    parser = argparse.ArgumentParser(description="Say hello")
    parser.add_argument(
        "-n", "--name", metavar="name", default="Tuyen", help="Name to greet"
    )
    return parser.parse_args()


def main():
    args = get_args()
    print("Hello, {}!".format(args.name))


if __name__ == "__main__":
    main()
