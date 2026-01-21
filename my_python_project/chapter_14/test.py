from subprocess import getoutput
import os

prg = "solution3.py"  # Run solution1.py with python3


def test_exists():
    """exists"""
    assert os.path.isfile(prg)


def test_usage():
    for flag in ["", "-h", "--help"]:
        out = getoutput(f"python3 {prg} {flag}")
        assert out.lower().startswith("usage")


def test_dog():
    """Test with custom word"""
    word = "dog"
    # Step 1: Choose any word
    out = getoutput(f"python3 {prg} {word}").splitlines()
    assert len(out) == 56

    assert out[0] == "blog"

    assert out[-1] == "zog"

    assert word not in out


def test_apple():
    """Test with custom word"""
    word = "apple"
    # Step 1: Choose any word
    out = getoutput(f"python3 {prg} {word}").splitlines()
    assert len(out) == 57
    assert out[0] == "bapple"
    assert out[-1] == "zapple"


def test_no_vowels():
    """Test word with no vowels"""
    out = getoutput(f"python3 {prg} ZYX")

    assert out == "Cannot rhyme with ZYX"


def test_uppercase():
    """Test uppercase"""
    out1 = getoutput(f"python3 {prg} APPLE").splitlines()
    out2 = getoutput(f"python3 {prg} apple").splitlines()

    assert out1 == out2
