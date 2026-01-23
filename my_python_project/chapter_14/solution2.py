#!/usr/bin/env python3
"""Make rhyming words - Solution 2 Refactored"""

import argparse
import string


# ============================================================
# PURE FUNCTIONS
# ============================================================


def get_prefixes():
    """Get list of consonant prefixes."""
    single_consonants = list("bcdfghjklmnpqrstvwxyz")
    consonant_clusters = (
        "bl br ch cl cr dr fl fr gl gr pl pr sc "
        "sh sk sl sm sn sp st sw th tr tw thw wh wr "
        "sch scr shr sph spl spr squ str thr"
    ).split()

    return single_consonants + consonant_clusters


def stemmer(word):
    """
    Split word into consonant prefix and rest (iterative approach).

    Args:
        word (str): Word to stem

    Returns:
        tuple: (consonant_prefix, rest_of_word)
    """
    word = word.lower().strip(string.punctuation)

    # Handle empty string
    if not word:
        return ("", "")

    start_chars = []

    for i, char in enumerate(word):
        if char in "aeiou":
            # Found first vowel
            return ("".join(start_chars), word[i:])
        else:
            start_chars.append(char)

    # No vowel found
    return ("".join(start_chars), "")


def create_rhymes(rest, start, prefixes):
    """Create list of rhyming words."""
    rhymes = [prefix + rest for prefix in prefixes if prefix != start]
    return sorted(rhymes)


def format_rhymes_output(rhymes):
    """Format list of rhymes as string."""
    return "\n".join(rhymes)


def format_no_rhyme_message(word):
    """Format error message."""
    return f"Cannot rhyme with {word}"


# ============================================================
# ARGPARSE FUNCTION
# ============================================================


def get_args():
    """Get command-line arguments."""
    parser = argparse.ArgumentParser(description='Make rhyming "words"')
    parser.add_argument("text", metavar="word", help="A word to rhyme")
    return parser.parse_args()


# ============================================================
# MAIN FUNCTION
# ============================================================


def main():
    """Main program flow."""
    args = get_args()
    prefixes = get_prefixes()
    start, rest = stemmer(args.text)

    if rest:
        rhymes = create_rhymes(rest, start, prefixes)
        output = format_rhymes_output(rhymes)
    else:
        output = format_no_rhyme_message(args.text)

    print(output)


if __name__ == "__main__":
    main()
