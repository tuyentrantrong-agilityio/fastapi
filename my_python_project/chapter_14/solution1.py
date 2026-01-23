#!/usr/bin/env python3
"""Make rhyming words - Refactored for unit testing"""

import argparse
import re
import string


# ============================================================
# PURE FUNCTIONS - Easy to test
# ============================================================


def get_prefixes():
    """
    Get list of consonant prefixes for rhyming.

    Returns:
        list: List of consonant strings (single and clusters)

    Examples:
        >>> prefixes = get_prefixes()
        >>> 'b' in prefixes
        True
        >>> 'ch' in prefixes
        True
        >>> len(prefixes)
        57
    """
    single_consonants = list("bcdfghjklmnpqrstvwxyz")
    consonant_clusters = (
        "bl br ch cl cr dr fl fr gl gr pl pr sc "
        "sh sk sl sm sn sp st sw th tr tw thw wh wr "
        "sch scr shr sph spl spr squ str thr"
    ).split()

    return single_consonants + consonant_clusters


def stemmer(word):
    """
    Split word into consonant prefix and rest.

    Args:
        word (str): Word to stem

    Returns:
        tuple: (consonant_prefix, rest_of_word)

    Examples:
        >>> stemmer("cake")
        ('c', 'ake')
        >>> stemmer("apple")
        ('', 'apple')
        >>> stemmer("CHAIR")
        ('ch', 'air')
    """
    word = word.lower().strip(string.punctuation)
    result = re.match(r"^([^aeiou]+)?(.*)$", word)

    if result:
        return (result.group(1) or "", result.group(2))
    else:
        return (word, "")


def create_rhymes(rest, start, prefixes):
    """
    Create list of rhyming words.

    Args:
        rest (str): The rhyming part (e.g., "ake" from "cake")
        start (str): Original prefix to exclude (e.g., "c")
        prefixes (list): List of all possible prefixes

    Returns:
        list: Sorted list of rhyming words

    Examples:
        >>> prefixes = ['b', 'c', 'f']
        >>> create_rhymes('ake', 'c', prefixes)
        ['bake', 'fake']
    """
    rhymes = [prefix + rest for prefix in prefixes if prefix != start]
    return sorted(rhymes)


def format_rhymes_output(rhymes):
    """
    Format list of rhymes as output string.

    Args:
        rhymes (list): List of rhyming words

    Returns:
        str: Formatted output (one word per line)

    Examples:
        >>> format_rhymes_output(['bake', 'cake', 'fake'])
        'bake\\ncake\\nfake'
    """
    return "\n".join(rhymes)


def format_no_rhyme_message(word):
    """
    Format error message when word cannot be rhymed.

    Args:
        word (str): The original word

    Returns:
        str: Error message

    Examples:
        >>> format_no_rhyme_message("xyz")
        'Cannot rhyme with xyz'
    """
    return f"Cannot rhyme with {word}"


# ============================================================
# ARGPARSE FUNCTION
# ============================================================


def get_args():
    """
    Get command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Make rhyming "words"')
    parser.add_argument("text", metavar="word", help="A word to rhyme")
    return parser.parse_args()


# ============================================================
# MAIN FUNCTION
# ============================================================


def main():
    """
    Main program flow.
    """
    # Get inputs
    args = get_args()
    prefixes = get_prefixes()

    # Process word
    start, rest = stemmer(args.text)

    # Generate output
    if rest:
        rhymes = create_rhymes(rest, start, prefixes)
        output = format_rhymes_output(rhymes)
    else:
        output = format_no_rhyme_message(args.text)

    # Display result
    print(output)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
