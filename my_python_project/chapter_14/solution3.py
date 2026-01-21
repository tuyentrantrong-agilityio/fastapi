"""Make rhyming words"""

import argparse
import io


def get_args():
    """get command-line arguments"""

    parser = argparse.ArgumentParser(description='Make rhyming "words"')
    parser.add_argument("text", metavar="word", help="A word to rhyme")

    parser.add_argument(
        "-w",
        "--wordlist",
        metavar="FILE",
        type=argparse.FileType("r"),
        default=None,
        help="Wordlist file",
    )

    return parser.parse_args()


# -------------------------------------------------
def read_wordlist(file_obj):
    """Read wordlist from file"""
    if file_obj:
        return set(word.strip().lower() for word in file_obj)
    return set()


def main():
    args = get_args()

    prefixes = (
        list("bcdfghjklmnpqrstvwxyz")
        + (
            "bl br ch cl cr dr fl fr gl gr pl pr sc "
            "sh sk sl sm sn sp st sw th tr tw thw wh wr "
            "sch scr shr sph spl spr squ str thr"
        ).split()
    )

    dict_words = read_wordlist(args.wordlist)

    start, rest = stemmer(args.text)

    if rest:
        rhymes = [p + rest for p in prefixes if p != start]
        print("\n".join(sorted(rhymes)))
    else:
        print(f"Cannot rhyme with {args.text}")


# -------------------------------------------------
def stemmer(word):
    """stem the word"""
    word = word.lower()
    vowel_pos = []
    for i in "aeiou":
        if i in word:
            vowel_pos.append(word.index(i))
    if vowel_pos:
        min_index = min(vowel_pos)
        return (word[:min_index], word[min_index:])
    else:
        return (word, "")


# --------------------------------------------------
def test_stemmer():
    """test the stemmer"""

    assert stemmer("") == ("", "")
    assert stemmer("cake") == ("c", "ake")
    assert stemmer("chair") == ("ch", "air")
    assert stemmer("APPLE") == ("", "apple")
    assert stemmer("RDNZL") == ("rdnzl", "")


# --------------------------------------------------
if __name__ == "__main__":
    main()
