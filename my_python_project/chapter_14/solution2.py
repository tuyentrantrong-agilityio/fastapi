"""Make rhyming words"""

import argparse
import string


def get_args():
    """get command-line argurments"""

    parser = argparse.ArgumentParser(description='Make rhyming "words"')
    parser.add_argument("text", metavar="word", default="word", help="A word to rhyme")

    return parser.parse_args()


# -------------------------------------------------
def main():
    args = get_args()

    prefixex = (
        list("bcdfghjklmnpqrstvwxyz")
        + (
            "bl br ch cl cr dr fl fr gl gr pl pr sc "
            "sh sk sl sm sn sp st sw th tr tw thw wh wr "
            "sch scr shr sph spl spr squ str thr"
        ).split()
    )
    start, rest = stemmer(args.text)

    if rest:
        print("\n".join(sorted([p + rest for p in prefixex if p != start])))
    else:
        print(f"Cannot rhyme with {args.text}")


# -------------------------------------------------
def stemmer(word):
    """stem the word"""
    word = word.lower().strip(string.punctuation)
    start = []

    for i in range(len(word)):
        if word[i] in "aeiou":
            # print("".join(start), word[i:])
            return ("".join(start), word[i:])
        else:
            start.append(word[i])
            if i == len(word) - 1:
                return ("".join(start), "")


# --------------------------------------------------
def test_stemmer():
    """test the stemmer"""

    assert stemmer("") == ("", "")
    assert stemmer("cake") == ("c", "ake")
    assert stemmer("chair") == ("ch", "air")
    assert stemmer("APPLE") == ("", "apple")
    assert stemmer("RDNZL") == ("rdnzl", "")


# -------------------------------------------------
if __name__ == "__main__":
    main()
