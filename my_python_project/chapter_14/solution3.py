#!/usr/bin/env python3
"""Make rhyming words with wordlist - Solution 3 Refactored"""

import argparse
from typing import Set, List, Optional


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
    Split word into consonant prefix and rest.
    
    Args:
        word (str): Word to stem
    
    Returns:
        tuple: (consonant_prefix, rest_of_word)
    """
    word = word.lower()
    
    # Handle empty string
    if not word:
        return ("", "")
    
    # Find positions of all vowels
    vowel_positions = [word.index(vowel) for vowel in "aeiou" if vowel in word]
    
    if vowel_positions:
        min_index = min(vowel_positions)
        return (word[:min_index], word[min_index:])
    else:
        # No vowels
        return (word, "")


def read_wordlist(file_obj):
    """
    Read wordlist from file object.
    
    Args:
        file_obj: File object or None
    
    Returns:
        set: Set of lowercase words
    
    Examples:
        >>> from io import StringIO
        >>> f = StringIO("Apple\\nBanana\\napple")
        >>> read_wordlist(f)
        {'apple', 'banana'}
    """
    if file_obj is None:
        return set()
    
    return set(word.strip().lower() for word in file_obj)


def create_rhymes(rest, start, prefixes):
    """
    Create list of rhyming words.
    
    Args:
        rest (str): The rhyming part
        start (str): Original prefix to exclude
        prefixes (list): List of possible prefixes
    
    Returns:
        list: Sorted list of rhyming words
    """
    rhymes = [prefix + rest for prefix in prefixes if prefix != start]
    return sorted(rhymes)


def filter_by_wordlist(rhymes, wordlist):
    """
    Filter rhymes to only include words in wordlist.
    
    Args:
        rhymes (list): List of potential rhymes
        wordlist (set): Set of valid words (empty = accept all)
    
    Returns:
        list: Filtered list of rhymes
    
    Examples:
        >>> filter_by_wordlist(['bake', 'cake', 'fake'], {'bake', 'cake'})
        ['bake', 'cake']
        >>> filter_by_wordlist(['bake', 'cake'], set())
        ['bake', 'cake']
    """
    if not wordlist:
        return rhymes
    
    return [word for word in rhymes if word in wordlist]


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
    parser.add_argument(
        "-w",
        "--wordlist",
        metavar="FILE",
        type=argparse.FileType("r"),
        default=None,
        help="Wordlist file",
    )
    return parser.parse_args()


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    """Main program flow."""
    # Get inputs
    args = get_args()
    prefixes = get_prefixes()
    wordlist = read_wordlist(args.wordlist)
    
    # Process word
    start, rest = stemmer(args.text)
    
    # Generate output
    if rest:
        rhymes = create_rhymes(rest, start, prefixes)
        
        # Filter by wordlist if provided
        if wordlist:
            rhymes = filter_by_wordlist(rhymes, wordlist)
        
        output = format_rhymes_output(rhymes)
    else:
        output = format_no_rhyme_message(args.text)
    
    # Display result
    print(output)


if __name__ == "__main__":
    main()