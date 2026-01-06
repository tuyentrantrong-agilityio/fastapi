"""Make rhyming words"""

import argparse
import io
from pydash import flatten


def get_args():
    """get command-line arguments"""  # ← SỬA lỗi 3

    parser = argparse.ArgumentParser(description='Make rhyming "words"')
    parser.add_argument("text", metavar="word", help="A word to rhyme")

    parser.add_argument(
        "-w",
        "--wordlist",
        metavar="FILE",
        type=argparse.FileType('r'),  # ← SỬA lỗi 5
        default="/usr/share/dict/words",
        help="Wordlist file",
    )

    return parser.parse_args()


# -------------------------------------------------
def main():
    args = get_args()

    prefixes = (  # ← SỬA lỗi 1
        list("bcdfghjklmnpqrstvwxyz")
        + (
            "bl br ch cl cr dr fl fr gl gr pl pr sc "
            "sh sk sl sm sn sp st sw th tr tw thw wh wr "
            "sch scr shr sph spl spr squ str thr"
        ).split()
    )
    
    dict_words = read_wordlist(args.wordlist)

    def is_dict_word(word):
        return word.lower() in dict_words if dict_words else True

    start, rest = stemmer(args.text)

    if rest:
        rhymes = [p + rest for p in prefixes if p != start]  # ← SỬA lỗi 1
        valid_rhymes = filter(is_dict_word, rhymes)  # ← SỬA lỗi 6
        print("\n".join(sorted(valid_rhymes)))
    else:
        print(f"Cannot rhyme with {args. text}")


# -------------------------------------------------
def stemmer(word):
    """stem the word"""
    word = word.lower()
    vowel_pos = []  # ← SỬA lỗi 2
    for i in "aeiou": 
        if i in word:
            vowel_pos.append(word.index(i))  # ← SỬA lỗi 2
    
    if vowel_pos:  # ← SỬA lỗi 2
        min_index = min(vowel_pos)  # ← SỬA lỗi 2
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
def read_wordlist(fh):
    """Read the wordlist file"""

    return set(flatten([line.lower().strip().split() for line in fh] if fh else []))


# --------------------------------------------------
def test_read_wordlist():  # ← SỬA lỗi 4
    """test the read_wordlist function"""

    assert read_wordlist(io.StringIO("foo\nbar\nfoo\n")) == set(["foo", "bar"])
    assert read_wordlist(io.StringIO("foo bar\nbar foo\nfoo")) == set(["foo", "bar"])


# -------------------------------------------------
if __name__ == "__main__": 
    main()